package com.company.product.common.exception;

import com.company.product.common.web.ApiResult;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.BindException;
import org.springframework.web.bind.MissingRequestHeaderException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.HandlerMethodValidationException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.HandlerMapping;
import org.springframework.web.servlet.NoHandlerFoundException;
import org.springframework.web.servlet.resource.NoResourceFoundException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.server.ResponseStatusException;

import java.util.stream.Collectors;

/**
 * 全局异常处理（样板）。诊断主事件只在此边界记录一次；日志勿输出敏感参数。
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResult<Void>> handleBusiness(BusinessException ex, HttpServletRequest request) {
        String traceId = MDC.get("traceId");
        log.warn(
                "event=business.request.rejected traceId={} errorCode={} httpStatus={} method={} path={} exceptionType={}",
                traceId,
                ex.getErrorCode(),
                ex.getHttpStatus().value(),
                request.getMethod(),
                routePath(request),
                ex.getClass().getName(),
                ex
        );
        return ResponseEntity
                .status(ex.getHttpStatus())
                .body(ApiResult.fail(ex.getHttpStatus().value(), ex.getMessage(), ex.getErrorCode(), traceId));
    }

    @ExceptionHandler({
            BindException.class,
            MethodArgumentNotValidException.class,
            HandlerMethodValidationException.class,
            ConstraintViolationException.class,
            MethodArgumentTypeMismatchException.class,
            HttpMessageNotReadableException.class,
            MissingServletRequestParameterException.class,
            MissingRequestHeaderException.class
    })
    public ResponseEntity<ApiResult<Void>> handleValidation(Exception ex, HttpServletRequest request) {
        String traceId = MDC.get("traceId");
        log.warn(
                "event=request.validation.failed traceId={} errorCode={} httpStatus={} method={} path={} exceptionType={} validation={}",
                traceId,
                ErrorCodes.VALIDATION_FAILED,
                HttpStatus.BAD_REQUEST.value(),
                request.getMethod(),
                routePath(request),
                ex.getClass().getName(),
                validationSummary(ex)
        );
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResult.fail(
                        HttpStatus.BAD_REQUEST.value(),
                        "请求参数不合法",
                        ErrorCodes.VALIDATION_FAILED,
                        traceId
                ));
    }

    @ExceptionHandler({
            ResponseStatusException.class,
            NoHandlerFoundException.class,
            NoResourceFoundException.class
    })
    public ResponseEntity<ApiResult<Void>> handleClientStatus(Exception ex, HttpServletRequest request) {
        HttpStatus status = clientStatus(ex);
        if (status == null) {
            return handleUnknown(ex, request);
        }
        String traceId = MDC.get("traceId");
        String errorCode = clientErrorCode(status);
        log.warn(
                "event=client.request.rejected traceId={} errorCode={} httpStatus={} method={} path={} exceptionType={}",
                traceId,
                errorCode,
                status.value(),
                request.getMethod(),
                routePath(request),
                ex.getClass().getName()
        );
        return ResponseEntity
                .status(status)
                .body(ApiResult.fail(status.value(), clientMessage(status), errorCode, traceId));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResult<Void>> handleUnknown(Exception ex, HttpServletRequest request) {
        String traceId = MDC.get("traceId");
        log.error(
                "event=system.unhandled.failed traceId={} errorCode={} httpStatus={} method={} path={} exceptionType={}",
                traceId,
                ErrorCodes.INTERNAL_ERROR,
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                request.getMethod(),
                routePath(request),
                ex.getClass().getName(),
                ex
        );
        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResult.fail(500, "系统繁忙", ErrorCodes.INTERNAL_ERROR, traceId));
    }

    private static String routePath(HttpServletRequest request) {
        Object pattern = request.getAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE);
        if (pattern instanceof String route && !route.isBlank()) {
            return route;
        }
        String uri = request.getRequestURI();
        int query = uri.indexOf('?');
        return query >= 0 ? uri.substring(0, query) : uri;
    }

    private static HttpStatus clientStatus(Exception ex) {
        if (ex instanceof NoHandlerFoundException || ex instanceof NoResourceFoundException) {
            return HttpStatus.NOT_FOUND;
        }
        if (ex instanceof ResponseStatusException responseStatus
                && responseStatus.getStatusCode() instanceof HttpStatus status
                && isTrackedClientStatus(status)) {
            return status;
        }
        return null;
    }

    private static boolean isTrackedClientStatus(HttpStatus status) {
        return status == HttpStatus.UNAUTHORIZED
                || status == HttpStatus.FORBIDDEN
                || status == HttpStatus.NOT_FOUND
                || status == HttpStatus.TOO_MANY_REQUESTS;
    }

    private static String clientErrorCode(HttpStatus status) {
        if (status == HttpStatus.UNAUTHORIZED) {
            return ErrorCodes.UNAUTHENTICATED;
        }
        if (status == HttpStatus.FORBIDDEN) {
            return ErrorCodes.ACCESS_DENIED;
        }
        if (status == HttpStatus.TOO_MANY_REQUESTS) {
            return ErrorCodes.RATE_LIMITED;
        }
        return ErrorCodes.NOT_FOUND;
    }

    private static String clientMessage(HttpStatus status) {
        if (status == HttpStatus.UNAUTHORIZED) {
            return "未登录";
        }
        if (status == HttpStatus.FORBIDDEN) {
            return "无权限";
        }
        if (status == HttpStatus.TOO_MANY_REQUESTS) {
            return "请求过于频繁";
        }
        return "资源不存在";
    }

    private static String validationSummary(Exception ex) {
        if (ex instanceof BindException bindException) {
            return bindException.getBindingResult().getFieldErrors().stream()
                    .map(error -> error.getField() + ":" + error.getCode())
                    .distinct()
                    .sorted()
                    .collect(Collectors.joining(","));
        }
        if (ex instanceof HandlerMethodValidationException methodValidation) {
            return methodValidation.getParameterValidationResults().stream()
                    .map(result -> {
                        String name = result.getMethodParameter().getParameterName();
                        String parameter = name == null
                                ? "arg" + result.getMethodParameter().getParameterIndex()
                                : name;
                        return parameter + ":constraint";
                    })
                    .distinct()
                    .sorted()
                    .collect(Collectors.joining(","));
        }
        if (ex instanceof ConstraintViolationException constraintViolationException) {
            return constraintViolationException.getConstraintViolations().stream()
                    .map(violation -> violation.getPropertyPath() + ":"
                            + violation.getConstraintDescriptor().getAnnotation().annotationType().getSimpleName())
                    .distinct()
                    .sorted()
                    .collect(Collectors.joining(","));
        }
        if (ex instanceof MethodArgumentTypeMismatchException mismatchException) {
            return mismatchException.getName() + ":typeMismatch";
        }
        if (ex instanceof MissingServletRequestParameterException missingParameter) {
            return missingParameter.getParameterName() + ":required";
        }
        if (ex instanceof MissingRequestHeaderException missingHeader) {
            return missingHeader.getHeaderName() + ":required";
        }
        if (ex instanceof HttpMessageNotReadableException) {
            return "requestBody:malformed";
        }
        return "request:invalid";
    }
}
