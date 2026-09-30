package com.company.product.modules.system.api.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

/**
 * 普通更新只允许改邮箱。状态须走单独的受权接口。
 * version 是打开详情时读到的乐观锁版本，不能改成提交前重新查询到的最新值。
 */
public record UserUpdateRequest(
        @NotNull @Email String email,
        @NotNull @Min(0) Integer version
) {
}
