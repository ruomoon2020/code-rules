package com.company.product.modules.system.api;

import com.company.product.common.observability.TraceIdFilter;
import com.company.product.common.web.ApiResult;
import com.company.product.common.web.PageResponse;
import com.company.product.modules.system.api.dto.UserCreateRequest;
import com.company.product.modules.system.api.dto.UserDetailResponse;
import com.company.product.modules.system.api.dto.UserPageQuery;
import com.company.product.modules.system.api.dto.UserSummaryResponse;
import com.company.product.modules.system.api.dto.UserUpdateRequest;
import com.company.product.modules.system.application.UserService;
import jakarta.validation.Valid;
import org.slf4j.MDC;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 用户 API（样板）。禁止注入 UserMapper。
 */
@RestController
@RequestMapping("/api/v1/system/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public ApiResult<PageResponse<UserSummaryResponse>> page(@Valid UserPageQuery query) {
        return ApiResult.ok(userService.page(query), traceId());
    }

    @GetMapping("/{id}")
    public ApiResult<UserDetailResponse> detail(@PathVariable long id) {
        return ApiResult.ok(userService.detail(id), traceId());
    }

    @PostMapping
    public ApiResult<UserDetailResponse> create(@Valid @RequestBody UserCreateRequest request) {
        return ApiResult.ok(userService.create(request), traceId());
    }

    @PutMapping("/{id}")
    public ApiResult<UserDetailResponse> update(
            @PathVariable long id,
            @Valid @RequestBody UserUpdateRequest request
    ) {
        return ApiResult.ok(userService.update(id, request), traceId());
    }

    @DeleteMapping("/{id}")
    public ApiResult<Void> delete(@PathVariable long id) {
        userService.delete(id);
        return ApiResult.ok(null, traceId());
    }

    private static String traceId() {
        return MDC.get(TraceIdFilter.MDC_KEY);
    }
}
