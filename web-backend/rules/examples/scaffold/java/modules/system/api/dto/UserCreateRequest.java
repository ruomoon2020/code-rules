package com.company.product.modules.system.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record UserCreateRequest(
        @NotBlank @Size(min = 2, max = 32) String username,
        String email
) {
}
