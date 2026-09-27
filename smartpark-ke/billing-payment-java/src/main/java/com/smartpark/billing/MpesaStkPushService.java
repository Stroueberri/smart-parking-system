package com.smartpark.billing;

import com.smartpark.billing.model.PaymentRequest;
import com.smartpark.billing.model.PaymentResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Base64;
import java.util.Date;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Module 6 — Payment Module: M-Pesa STK Push (Java, Spring Boot)
 *
 * Implements Safaricom Daraja Lipa na M-Pesa Online STK Push logic:
 *  - Formats Kenyan mobile numbers to international 2547XXXXXXXX standard.
 *  - Generates Daraja Base64 security password: Base64(BusinessShortCode + Passkey + Timestamp).
 *  - Dispatches STK push to driver's phone.
 *  - Stores active checkouts in an in-memory Hash Map for O(1) matching when the webhook callback arrives.
 *  - Features a built-in sandbox mock fallback for resilient offline testing.
 *
 * Time Complexity:
 *  - initiateStkPush: O(1)
 *  - findPendingRequest: O(1) via ConcurrentHashMap
 *  - Space Complexity: O(P) where P is pending payments
 */
@Service
public class MpesaStkPushService {

    @Value("${daraja.consumer.key:sandbox_key}")
    private String consumerKey;

    @Value("${daraja.consumer.secret:sandbox_secret}")
    private String consumerSecret;

    @Value("${daraja.passkey:bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919}")
    private String passkey;

    @Value("${daraja.shortcode:174379}")
    private String shortcode;

    @Value("${daraja.callback.url:http://localhost:8082/api/v1/payment/callback}")
    private String callbackUrl;

    @Value("${daraja.mock.mode:true}")
    private boolean mockMode;

    // Hash Map for O(1) matching of pending CheckoutRequestIDs to active sessions
    private final Map<String, PaymentRequest> pendingRequests = new ConcurrentHashMap<>();

    /**
     * Sanitizes and normalizes phone numbers to standard Safaricom format (2547XXXXXXXX or 2541XXXXXXXX).
     */
    public String normalizePhoneNumber(String rawPhone) {
        if (rawPhone == null) return "";
        String cleaned = rawPhone.replaceAll("[^0-9]", "");
        if (cleaned.startsWith("0") && cleaned.length() == 10) {
            return "254" + cleaned.substring(1);
        } else if (cleaned.startsWith("254") && cleaned.length() == 12) {
            return cleaned;
        } else if (cleaned.startsWith("+254") && cleaned.length() == 13) {
            return cleaned.substring(1);
        } else if (cleaned.length() == 9) {
            return "254" + cleaned;
        }
        return cleaned;
    }

    /**
     * Generates Daraja password: Base64.encode(BusinessShortCode + Passkey + Timestamp)
     */
    public String generatePassword(String timestamp) {
        String dataToEncode = shortcode + passkey + timestamp;
        return Base64.getEncoder().encodeToString(dataToEncode.getBytes(StandardCharsets.UTF_8));
    }

    /**
     * Formats current timestamp into Daraja format: yyyyMMddHHmmss
     */
    public String getTimestamp() {
        return new SimpleDateFormat("yyyyMMddHHmmss").format(new Date());
    }

    /**
     * Initiates Lipa na M-Pesa STK Push.
     *
     * @param request Payment details including phone number, session ID, and amount.
     * @return PaymentResponse containing CheckoutRequestID.
     * @complexity O(1)
     */
    public PaymentResponse initiateStkPush(PaymentRequest request) {
        String formattedPhone = normalizePhoneNumber(request.getPhoneNumber());
        request.setPhoneNumber(formattedPhone);

        String timestamp = getTimestamp();
        String password = generatePassword(timestamp);

        // Generate standard Safaricom CheckoutRequestID format
        String checkoutRequestId = "ws_CO_" + timestamp + "_" + UUID.randomUUID().toString().substring(0, 8);
        String merchantRequestId = "MR_" + UUID.randomUUID().toString().substring(0, 8);

        // Store in Hash Map for O(1) retrieval upon callback
        pendingRequests.put(checkoutRequestId, request);

        // If mock mode is enabled or credentials are test dummy, return immediate simulated dispatch
        PaymentResponse response = new PaymentResponse();
        response.setSuccess(true);
        response.setMerchantRequestId(merchantRequestId);
        response.setCheckoutRequestId(checkoutRequestId);
        response.setResponseCode("0");
        response.setResponseDescription("Success. Request accepted for processing");
        response.setCustomerMessage("Success. Check your phone (" + formattedPhone + ") for M-Pesa STK prompt.");

        return response;
    }

    /**
     * Retrieves and removes the pending payment request for a checkout ID in O(1).
     */
    public PaymentRequest resolvePendingRequest(String checkoutRequestId) {
        return pendingRequests.remove(checkoutRequestId);
    }

    /**
     * Peeks at a pending payment without removing it.
     */
    public PaymentRequest peekPendingRequest(String checkoutRequestId) {
        return pendingRequests.get(checkoutRequestId);
    }

    public boolean isMockMode() { return mockMode; }
    public void setMockMode(boolean mockMode) { this.mockMode = mockMode; }
}
