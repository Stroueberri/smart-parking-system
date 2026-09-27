package com.smartpark.billing.model;

/**
 * DTO for Fee calculation output.
 */
public class FeeResponse {
    private int durationMinutes;
    private double fee;
    private String tariffApplied;
    private String formattedDuration;

    public FeeResponse() {}

    public FeeResponse(int durationMinutes, double fee, String tariffApplied, String formattedDuration) {
        this.durationMinutes = durationMinutes;
        this.fee = fee;
        this.tariffApplied = tariffApplied;
        this.formattedDuration = formattedDuration;
    }

    public int getDurationMinutes() { return durationMinutes; }
    public void setDurationMinutes(int durationMinutes) { this.durationMinutes = durationMinutes; }

    public double getFee() { return fee; }
    public void setFee(double fee) { this.fee = fee; }

    public String getTariffApplied() { return tariffApplied; }
    public void setTariffApplied(String tariffApplied) { this.tariffApplied = tariffApplied; }

    public String getFormattedDuration() { return formattedDuration; }
    public void setFormattedDuration(String formattedDuration) { this.formattedDuration = formattedDuration; }
}
