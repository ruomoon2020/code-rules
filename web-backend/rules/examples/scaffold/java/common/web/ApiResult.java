package com.company.product.common.web;

/**
 * 统一 API 响应（样板）。成功 code=0；失败由 GlobalExceptionHandler 填充 errorCode。
 */
public record ApiResult<T>(
        int code,
        String message,
        String traceId,
        String errorCode,
        T data
) {
    public static <T> ApiResult<T> ok(T data, String traceId) {
        return new ApiResult<>(0, "ok", traceId, null, data);
    }

    public static <T> ApiResult<T> fail(int code, String message, String errorCode, String traceId) {
        return new ApiResult<>(code, message, traceId, errorCode, null);
    }
}
