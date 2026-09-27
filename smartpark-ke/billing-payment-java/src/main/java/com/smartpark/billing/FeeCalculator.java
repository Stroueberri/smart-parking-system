package com.smartpark.billing;

import com.smartpark.billing.model.FeeResponse;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Module 5 — Fee Calculation Module (Java)
 *
 * Implements the fixed tariff table and dynamic data-driven tariff evaluations.
 *
 * Data Structure:
 *  Linear Lookup Array / Table of (upper_bound_minutes, fee) tuples.
 *  Because the tariff tiers are small and fixed in size (e.g. 5 tiers),
 *  scanning the array performs in O(1) constant time.
 *  Dynamic runtime updates are supported via a thread-safe CopyOnWriteArrayList.
 *
 * Time Complexity:
 *  - calculateFee: O(T) where T is number of tiers, O(1) in practice.
 *  - Space Complexity: O(T)
 */
@Service
public class FeeCalculator {

    /**
     * Immutable representation of a Tariff Tier.
     */
    public static class TariffTier {
        private final int maxMinutes;
        private final double fee;
        private final String description;

        public TariffTier(int maxMinutes, double fee, String description) {
            this.maxMinutes = maxMinutes;
            this.fee = fee;
            this.description = description;
        }

        public int getMaxMinutes() { return maxMinutes; }
        public double getFee() { return fee; }
        public String getDescription() { return description; }
    }

    // Dynamic, thread-safe tariff lookup table
    private final List<TariffTier> tariffTable = new CopyOnWriteArrayList<>();

    public FeeCalculator() {
        // Initialize default fixed tariff schedule per Section 1.8
        loadDefaultTariffs();
    }

    /**
     * Loads the default fixed schedule specified in Section 1.8.
     */
    public void loadDefaultTariffs() {
        tariffTable.clear();
        tariffTable.add(new TariffTier(30, 0.00, "Up to 30 minutes (Free)"));
        tariffTable.add(new TariffTier(120, 50.00, "Up to 2 hours (Kshs 50)"));
        tariffTable.add(new TariffTier(240, 100.00, "Up to 4 hours (Kshs 100)"));
        tariffTable.add(new TariffTier(360, 300.00, "Up to 6 hours (Kshs 300)"));
        tariffTable.add(new TariffTier(Integer.MAX_VALUE, 500.00, "Over 6 hours (Kshs 500)"));
    }

    /**
     * Updates the dynamic tariff table at runtime (e.g., from DB sync).
     * @param tiers List of new tariff tiers.
     */
    public void setDynamicTariffs(List<TariffTier> tiers) {
        List<TariffTier> sorted = new ArrayList<>(tiers);
        sorted.sort(Comparator.comparingInt(TariffTier::getMaxMinutes));
        tariffTable.clear();
        tariffTable.addAll(sorted);
    }

    /**
     * Calculates the parking fee for a given duration in minutes.
     *
     * Algorithm:
     *   Scan tariff lookup table linearly:
     *   for each tier in tariffTable:
     *       if durationMinutes <= tier.maxMinutes:
     *           return tier.fee
     *
     * @param durationMinutes Total elapsed parking duration in minutes.
     * @return FeeResponse containing amount due, applied tariff description, and formatted duration.
     * @complexity O(1)
     */
    public FeeResponse calculateFee(int durationMinutes) {
        if (durationMinutes < 0) {
            durationMinutes = 0;
        }

        double fee = 500.00; // default cap
        String appliedTier = "Over 6 hours (Kshs 500)";

        for (TariffTier tier : tariffTable) {
            if (durationMinutes <= tier.getMaxMinutes()) {
                fee = tier.getFee();
                appliedTier = tier.getDescription();
                break;
            }
        }

        String formatted = formatDuration(durationMinutes);
        return new FeeResponse(durationMinutes, fee, appliedTier, formatted);
    }

    /**
     * Formats duration into a clean human-readable string (e.g., "3h 15m").
     */
    public String formatDuration(int totalMinutes) {
        if (totalMinutes < 60) {
            return totalMinutes + " mins";
        }
        int hours = totalMinutes / 60;
        int mins = totalMinutes % 60;
        return hours + "h " + mins + "m";
    }

    public List<TariffTier> getTariffTable() {
        return Collections.unmodifiableList(tariffTable);
    }
}
