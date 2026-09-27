package com.company.product.modules.system.api.dto;

/**
 * 普通更新只允许改邮箱。状态须走单独的受权接口。
 */
public record UserUpdateRequest(
        String email
) {
}
