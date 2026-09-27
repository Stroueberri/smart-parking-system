package com.smartpark.billing;

import com.smartpark.billing.model.FeeResponse;
import com.smartpark.billing.model.PaymentRequest;
import com.smartpark.billing.model.PaymentResponse;
import com.smartpark.billing.model.StkCallbackPayload;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;

/**
 * REST Controller exposing Billing, Fee Calculation, STK Push initiation,
 * and Daraja Payment Webhook Callbacks.
 *
 * Backs Module 5 (Fee Calculation), Module 6 (M-Pesa STK Push), and Module 11 (Notifications).
 *
 * Data Structure:
 *  ConcurrentLinkedQueue<StkCallbackPayload> (FIFO Queue) ensuring incoming asynchronous
 *  payment webhooks are processed strictly in arrival order.
 */
@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "*")
public class PaymentCallbackController {

    private final FeeCalculator feeCalculator;
    private final MpesaStkPushService mpesaService;
    private final NotificationDispatcher notificationDispatcher;

    @Value("${gateway.url:http://localhost:5000}")
    private String gatewayUrl;

    // FIFO Queue of asynchronous payment callbacks
    private final ConcurrentLinkedQueue<StkCallbackPayload> callbackQueue = new ConcurrentLinkedQueue<>();
    private final List<StkCallbackPayload> processedCallbacks = Collections.synchronizedList(new ArrayList<>());

    private final RestTemplate restTemplate = new RestTemplate();

    @Autowired
    public PaymentCallbackController(FeeCalculator feeCalculator,
                                     MpesaStkPushService mpesaService,
                                     NotificationDispatcher notificationDispatcher) {
        this.feeCalculator = feeCalculator;
        this.mpesaService = mpesaService;
        this.notificationDispatcher = notificationDispatcher;
    }

    /**
     * Module 5: Fee Calculation endpoint.
     * GET /api/v1/fee/calculate?minutes=145
     */
    @GetMapping("/fee/calculate")
    public ResponseEntity<FeeResponse> calculateFee(@RequestParam("minutes") int minutes) {
        FeeResponse response = feeCalculator.calculateFee(minutes);
        return ResponseEntity.ok(response);
    }

    /**
     * Module 5: Retrieve active tariff schedule.
     */
    @GetMapping("/tariffs")
    public ResponseEntity<List<FeeCalculator.TariffTier>> getTariffs() {
        return ResponseEntity.ok(feeCalculator.getTariffTable());
    }

    /**
     * Module 6: STK Push Initiation endpoint.
     * POST /api/v1/payment/stk-push
     */
    @PostMapping("/payment/stk-push")
    public ResponseEntity<PaymentResponse> initiateStkPush(@RequestBody PaymentRequest request) {
        PaymentResponse response = mpesaService.initiateStkPush(request);
        return ResponseEntity.ok(response);
    }

    /**
     * Module 6: Safaricom Daraja Webhook Callback Receiver.
     * POST /api/v1/payment/callback
     */
    @PostMapping("/payment/callback")
    public ResponseEntity<Map<String, Object>> handleDarajaCallback(@RequestBody StkCallbackPayload callback) {
        // Enqueue into FIFO Queue to process in strict order of arrival
        callbackQueue.offer(callback);
        processCallbackQueue();

        Map<String, Object> ack = new HashMap<>();
        ack.put("ResultCode", 0);
        ack.put("ResultDesc", "Callback accepted for FIFO processing");
        return ResponseEntity.ok(ack);
    }

    /**
     * Dequeues and processes pending callbacks in FIFO order.
     */
    private synchronized void processCallbackQueue() {
        while (!callbackQueue.isEmpty()) {
            StkCallbackPayload payload = callbackQueue.poll();
            if (payload == null) break;

            processedCallbacks.add(payload);

            // Match by CheckoutRequestID in O(1)
            PaymentRequest origReq = mpesaService.resolvePendingRequest(payload.getCheckoutRequestId());
            int sessionId = (origReq != null) ? origReq.getSessionId() : 0;
            String plate = (origReq != null) ? origReq.getPlateNumber() : "UNKNOWN";
            String phone = (origReq != null) ? origReq.getPhoneNumber() : payload.getPhoneNumber();

            if (payload.getResultCode() == 0) {
                // Payment confirmed: trigger notification receipt
                if (payload.getMpesaReceiptNumber() == null || payload.getMpesaReceiptNumber().isEmpty()) {
                    payload.setMpesaReceiptNumber("QKE" + System.currentTimeMillis() % 10000000);
                }
                notificationDispatcher.enqueueReceipt(sessionId, phone, plate, payload.getAmount(), payload.getMpesaReceiptNumber());

                // Signal Python Gateway to confirm payment and open barrier
                signalGatewayBarrierOpen(sessionId, payload.getMpesaReceiptNumber(), payload.getAmount());
            }
        }
    }

    /**
     * Signals Python Gateway to mark session paid and trigger barrier actuator.
     */
    private void signalGatewayBarrierOpen(int sessionId, String receipt, double amount) {
        try {
            String url = gatewayUrl + "/api/payment/confirm-webhook";
            Map<String, Object> body = new HashMap<>();
            body.put("sessionId", sessionId);
            body.put("mpesaReceipt", receipt);
            body.put("amount", amount);
            body.put("paid", true);
            restTemplate.postForObject(url, body, String.class);
        } catch (Exception e) {
            System.err.println("[Java Service] Notice: Could not push callback directly to Gateway: " + e.getMessage());
        }
    }

    /**
     * Simulated test webhook trigger endpoint for end-to-end demo flows.
     */
    @PostMapping("/payment/simulate-success")
    public ResponseEntity<Map<String, Object>> simulateSuccess(@RequestParam("checkoutRequestId") String checkoutRequestId) {
        PaymentRequest origReq = mpesaService.peekPendingRequest(checkoutRequestId);
        double amount = (origReq != null) ? origReq.getAmount() : 50.0;
        String phone = (origReq != null) ? origReq.getPhoneNumber() : "254712345678";

        StkCallbackPayload simulated = new StkCallbackPayload();
        simulated.setCheckoutRequestId(checkoutRequestId);
        simulated.setMerchantRequestId("MR_SIMULATED");
        simulated.setResultCode(0);
        simulated.setResultDesc("The service was accepted successfully");
        simulated.setAmount(amount);
        simulated.setMpesaReceiptNumber("SIM" + UUID.randomUUID().toString().substring(0, 7).toUpperCase());
        simulated.setPhoneNumber(phone);

        return handleDarajaCallback(simulated);
    }

    /**
     * Health check endpoint.
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> map = new HashMap<>();
        map.put("status", "UP");
        map.put("service", "billing-payment-service");
        map.put("pendingCallbacksInQueue", callbackQueue.size());
        map.put("processedCallbacksCount", processedCallbacks.size());
        return ResponseEntity.ok(map);
    }
}
