package com.company.product.modules.system.api;

import com.company.product.common.observability.TraceIdFilter;
import com.company.product.common.web.ApiResult;
import com.company.product.common.web.PageResponse;
import com.company.product.modules.system.api.dto.UserCreateRequest;
import com.company.product.modules.system.api.dto.UserDeleteRequest;
import com.company.product.modules.system.api.dto.UserDetailResponse;
import com.company.product.modules.system.api.dto.UserPageQuery;
import com.company.product.modules.system.api.dto.UserSummaryResponse;
import com.company.product.modules.system.api.dto.UserUpdateRequest;
import com.company.product.modules.system.application.UserService;
import jakarta.validation.Valid;
import org.slf4j.MDC;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;

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
    @PreAuthorize("hasAuthority('system:user:read')")
    public ApiResult<PageResponse<UserSummaryResponse>> page(@Valid UserPageQuery query) {
        return ApiResult.ok(userService.page(query), traceId());
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('system:user:read')")
    public ApiResult<UserDetailResponse> detail(@PathVariable long id) {
        return ApiResult.ok(userService.detail(id), traceId());
    }

    @PostMapping
    @PreAuthorize("hasAuthority('system:user:create')")
    public ResponseEntity<ApiResult<UserDetailResponse>> create(@Valid @RequestBody UserCreateRequest request) {
        UserDetailResponse created = userService.create(request);
        return ResponseEntity
                .created(URI.create("/api/v1/system/users/" + created.id()))
                .body(ApiResult.ok(created, traceId()));
    }

    @PostMapping("/{id}/update")
    @PreAuthorize("hasAuthority('system:user:update')")
    public ApiResult<UserDetailResponse> update(
            @PathVariable long id,
            @Valid @RequestBody UserUpdateRequest request
    ) {
        return ApiResult.ok(userService.update(id, request), traceId());
    }

    @PostMapping("/{id}/delete")
    @PreAuthorize("hasAuthority('system:user:delete')")
    public ResponseEntity<Void> delete(
            @PathVariable long id,
            @Valid @RequestBody UserDeleteRequest request
    ) {
        userService.delete(id, request);
        return ResponseEntity.noContent()
                .header("X-Trace-Id", traceId())
                .build();
    }

    private static String traceId() {
        return MDC.get(TraceIdFilter.MDC_KEY);
    }
}
