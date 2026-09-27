package com.company.product.common.exception;

import org.springframework.http.HttpStatus;

/**
 * 业务异常（样板）。
 */
public class BusinessException extends RuntimeException {

    private final String errorCode;
    private final HttpStatus httpStatus;

    public BusinessException(String errorCode, String message) {
        this(errorCode, message, HttpStatus.BAD_REQUEST);
    }

    public BusinessException(String errorCode, String message, Throwable cause) {
        this(errorCode, message, HttpStatus.BAD_REQUEST, cause);
    }

    public BusinessException(String errorCode, String message, HttpStatus httpStatus) {
        super(message);
        require4xx(httpStatus);
        this.errorCode = requireErrorCode(errorCode);
        this.httpStatus = httpStatus;
    }

    public BusinessException(String errorCode, String message, HttpStatus httpStatus, Throwable cause) {
        super(message, cause);
        require4xx(httpStatus);
        this.errorCode = requireErrorCode(errorCode);
        this.httpStatus = httpStatus;
    }

    private static void require4xx(HttpStatus httpStatus) {
        if (httpStatus == null || !httpStatus.is4xxClientError()) {
            throw new IllegalArgumentException("BusinessException httpStatus must be 4xx");
        }
    }

    private static String requireErrorCode(String errorCode) {
        if (errorCode == null || errorCode.isBlank()) {
            throw new IllegalArgumentException("BusinessException errorCode must not be blank");
        }
        return errorCode;
    }

    public String getErrorCode() {
        return errorCode;
    }

    public HttpStatus getHttpStatus() {
        return httpStatus;
    }
}
