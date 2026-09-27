package com.company.product.modules.system.api.dto;

import java.time.Instant;

public record UserSummaryResponse(
        String id,
        String username,
        String status,
        Instant createdAt
) {
}
