package com.smartpark.billing.model;

/**
 * DTO for initiating Lipa na M-Pesa STK Push.
 */
public class PaymentRequest {
    private int sessionId;
    private String plateNumber;
    private String phoneNumber;
    private double amount;
    private String accountReference;

    public PaymentRequest() {}

    public PaymentRequest(int sessionId, String plateNumber, String phoneNumber, double amount, String accountReference) {
        this.sessionId = sessionId;
        this.plateNumber = plateNumber;
        this.phoneNumber = phoneNumber;
        this.amount = amount;
        this.accountReference = accountReference;
    }

    public int getSessionId() { return sessionId; }
    public void setSessionId(int sessionId) { this.sessionId = sessionId; }

    public String getPlateNumber() { return plateNumber; }
    public void setPlateNumber(String plateNumber) { this.plateNumber = plateNumber; }

    public String getPhoneNumber() { return phoneNumber; }
    public void setPhoneNumber(String phoneNumber) { this.phoneNumber = phoneNumber; }

    public double getAmount() { return amount; }
    public void setAmount(double amount) { this.amount = amount; }

    public String getAccountReference() { return accountReference; }
    public void setAccountReference(String accountReference) { this.accountReference = accountReference; }
}
