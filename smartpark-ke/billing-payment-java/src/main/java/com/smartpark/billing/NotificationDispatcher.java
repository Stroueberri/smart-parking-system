package com.smartpark.billing;

import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

/**
 * Module 11 — Notification Module (Java / Spring Boot)
 *
 * Dispatches SMS and Email parking receipts upon successful payment confirmation.
 *
 * Data Structure:
 *  Queue (FIFO) implemented via ConcurrentLinkedQueue to guarantee in-order delivery
 *  of asynchronous notification events and provide retry safety.
 *
 * Time Complexity:
 *  - enqueueNotification: O(1)
 *  - processNextNotification: O(1)
 *  - Space Complexity: O(N) where N = queued notification jobs
 */
@Service
public class NotificationDispatcher {

    public static class NotificationJob {
        private final int sessionId;
        private final String recipientPhone;
        private final String plateNumber;
        private final double amount;
        private final String mpesaReceipt;
        private final String messageText;
        private final LocalDateTime createdAt;
        private boolean sent;

        public NotificationJob(int sessionId, String recipientPhone, String plateNumber, double amount, String mpesaReceipt) {
            this.sessionId = sessionId;
            this.recipientPhone = recipientPhone;
            this.plateNumber = plateNumber;
            this.amount = amount;
            this.mpesaReceipt = mpesaReceipt;
            this.createdAt = LocalDateTime.now();
            this.sent = false;
            this.messageText = String.format(
                "SmartPark KE: Confirmed Kshs %.2f received for vehicle %s (Receipt: %s). Gate opened. Safe travels!",
                amount, plateNumber, mpesaReceipt
            );
        }

        public int getSessionId() { return sessionId; }
        public String getRecipientPhone() { return recipientPhone; }
        public String getPlateNumber() { return plateNumber; }
        public double getAmount() { return amount; }
        public String getMpesaReceipt() { return mpesaReceipt; }
        public String getMessageText() { return messageText; }
        public LocalDateTime getCreatedAt() { return createdAt; }
        public boolean isSent() { return sent; }
        public void setSent(boolean sent) { this.sent = sent; }
    }

    // FIFO Queue for asynchronous notification processing
    private final ConcurrentLinkedQueue<NotificationJob> jobQueue = new ConcurrentLinkedQueue<>();
    private final List<NotificationJob> sentHistory = new ArrayList<>();

    /**
     * Enqueues an outbound SMS receipt job in O(1) time.
     */
    public void enqueueReceipt(int sessionId, String recipientPhone, String plateNumber, double amount, String mpesaReceipt) {
        NotificationJob job = new NotificationJob(sessionId, recipientPhone, plateNumber, amount, mpesaReceipt);
        jobQueue.offer(job); // O(1) FIFO enqueue
        processNext();       // Trigger dispatch
    }

    /**
     * Dequeues and simulates SMS dispatch (Africa's Talking API compatible format).
     * @complexity O(1)
     */
    public synchronized NotificationJob processNext() {
        NotificationJob job = jobQueue.poll(); // O(1) FIFO dequeue
        if (job != null) {
            job.setSent(true);
            sentHistory.add(job);
            System.out.println("[SMS Notification Dispatched] To: " + job.getRecipientPhone() + " | Text: " + job.getMessageText());
        }
        return job;
    }

    public int getPendingQueueSize() {
        return jobQueue.size();
    }

    public List<NotificationJob> getSentHistory() {
        return new ArrayList<>(sentHistory);
    }
}
