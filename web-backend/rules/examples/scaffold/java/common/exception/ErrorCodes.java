package com.company.product.common.exception;

/**
 * 业务错误码集中维护（样板）。
 */
public final class ErrorCodes {

    private ErrorCodes() {}

    public static final String USER_NOT_FOUND = "USER_NOT_FOUND";
    public static final String AUDIT_LOG_NOT_FOUND = "AUDIT_LOG_NOT_FOUND";
    public static final String USERNAME_DUPLICATE = "USERNAME_DUPLICATE";
    public static final String CONCURRENT_MODIFICATION = "CONCURRENT_MODIFICATION";
    public static final String INVALID_SORT_FIELD = "INVALID_SORT_FIELD";
    public static final String TENANT_CONTEXT_MISSING = "TENANT_CONTEXT_MISSING";
    public static final String VALIDATION_FAILED = "VALIDATION_FAILED";
    public static final String UNAUTHENTICATED = "UNAUTHENTICATED";
    public static final String ACCESS_DENIED = "ACCESS_DENIED";
    public static final String NOT_FOUND = "NOT_FOUND";
    public static final String RATE_LIMITED = "RATE_LIMITED";
    public static final String INTERNAL_ERROR = "INTERNAL_ERROR";
}
