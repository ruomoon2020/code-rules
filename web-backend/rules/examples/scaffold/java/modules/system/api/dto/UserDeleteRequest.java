package com.company.product.modules.system.api.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

/**
 * version 是打开详情时读到的乐观锁版本。过期详情不能删掉刚被别人改过的行。
 */
public record UserDeleteRequest(
        @NotNull @Min(0) Integer version
) {
}
