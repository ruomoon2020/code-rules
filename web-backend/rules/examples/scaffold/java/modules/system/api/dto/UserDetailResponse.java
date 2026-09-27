package com.company.product.modules.system.api.dto;

import java.time.Instant;

public record UserDetailResponse(
        String id,
        String username,
        String status,
        String email,
        String phoneMasked,
        Instant createdAt
) {
}
