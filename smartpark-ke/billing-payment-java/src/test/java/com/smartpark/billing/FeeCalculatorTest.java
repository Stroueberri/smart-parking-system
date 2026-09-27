package com.smartpark.billing;

import com.smartpark.billing.model.FeeResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit Test Suite for Module 5: Fee Calculation Module.
 * Validates fixed tariff table compliance per Section 1.8.
 */
public class FeeCalculatorTest {

    private FeeCalculator feeCalculator;

    @BeforeEach
    public void setUp() {
        feeCalculator = new FeeCalculator();
    }

    @Test
    @DisplayName("Tier 1: Free up to 30 minutes grace period")
    public void testUpTo30MinutesFree() {
        assertEquals(0.00, feeCalculator.calculateFee(0).getFee());
        assertEquals(0.00, feeCalculator.calculateFee(15).getFee());
        assertEquals(0.00, feeCalculator.calculateFee(30).getFee());
    }

    @Test
    @DisplayName("Tier 2: Up to 2 hours (31 to 120 minutes) = Kshs 50")
    public void testUpTo2Hours() {
        assertEquals(50.00, feeCalculator.calculateFee(31).getFee());
        assertEquals(50.00, feeCalculator.calculateFee(60).getFee());
        assertEquals(50.00, feeCalculator.calculateFee(120).getFee());
    }

    @Test
    @DisplayName("Tier 3: Up to 4 hours (121 to 240 minutes) = Kshs 100")
    public void testUpTo4Hours() {
        assertEquals(100.00, feeCalculator.calculateFee(121).getFee());
        assertEquals(100.00, feeCalculator.calculateFee(180).getFee());
        assertEquals(100.00, feeCalculator.calculateFee(240).getFee());
    }

    @Test
    @DisplayName("Tier 4: Up to 6 hours (241 to 360 minutes) = Kshs 300")
    public void testUpTo6Hours() {
        assertEquals(300.00, feeCalculator.calculateFee(241).getFee());
        assertEquals(300.00, feeCalculator.calculateFee(300).getFee());
        assertEquals(300.00, feeCalculator.calculateFee(360).getFee());
    }

    @Test
    @DisplayName("Tier 5: Over 6 hours (> 360 minutes) = Kshs 500")
    public void testOver6Hours() {
        assertEquals(500.00, feeCalculator.calculateFee(361).getFee());
        assertEquals(500.00, feeCalculator.calculateFee(480).getFee());
        assertEquals(500.00, feeCalculator.calculateFee(1440).getFee());
    }

    @Test
    @DisplayName("Negative duration clamps safely to 0 (Free)")
    public void testNegativeDurationHandling() {
        FeeResponse res = feeCalculator.calculateFee(-10);
        assertEquals(0.00, res.getFee());
        assertEquals(0, res.getDurationMinutes());
    }

    @Test
    @DisplayName("Dynamic tariff update allows custom tiers")
    public void testDynamicTariffUpdate() {
        feeCalculator.setDynamicTariffs(List.of(
            new FeeCalculator.TariffTier(60, 20.00, "Custom: 1 hr promo"),
            new FeeCalculator.TariffTier(Integer.MAX_VALUE, 200.00, "Custom: Flat day rate")
        ));

        assertEquals(20.00, feeCalculator.calculateFee(45).getFee());
        assertEquals(200.00, feeCalculator.calculateFee(90).getFee());
    }
}
