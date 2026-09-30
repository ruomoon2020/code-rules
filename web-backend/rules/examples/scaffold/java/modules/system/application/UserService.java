package com.company.product.modules.system.application;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.core.toolkit.support.SFunction;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.company.product.common.audit.AuditContext;
import com.company.product.common.datascope.DataScope;
import com.company.product.common.datascope.DataScopePolicy;
import com.company.product.common.exception.BusinessException;
import com.company.product.common.exception.ErrorCodes;
import com.company.product.common.web.PageResponse;
import com.company.product.modules.system.api.dto.UserCreateRequest;
import com.company.product.modules.system.api.dto.UserDeleteRequest;
import com.company.product.modules.system.api.dto.UserDetailResponse;
import com.company.product.modules.system.api.dto.UserPageQuery;
import com.company.product.modules.system.api.dto.UserSummaryResponse;
import com.company.product.modules.system.api.dto.UserUpdateRequest;
import com.company.product.modules.system.application.audit.AuditRecordCommand;
import com.company.product.modules.system.application.audit.AuditRecorder;
import com.company.product.modules.system.application.converter.UserConverter;
import com.company.product.modules.system.domain.User;
import com.company.product.modules.system.infrastructure.mapper.UserMapper;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.Instant;
import java.util.Map;

@Service
public class UserService {

    private static final Map<String, SFunction<User, ?>> SORT_WHITELIST = Map.of(
            "createdAt", User::getCreatedAt
    );

    private final UserMapper userMapper;
    private final UserConverter userConverter;
    private final AuditRecorder auditRecorder;

    public UserService(UserMapper userMapper, UserConverter userConverter, AuditRecorder auditRecorder) {
        this.userMapper = userMapper;
        this.userConverter = userConverter;
        this.auditRecorder = auditRecorder;
    }

    @Transactional(readOnly = true)
    public PageResponse<UserSummaryResponse> page(UserPageQuery query) {
        Page<User> page = new Page<>(query.page(), query.pageSize());
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        if (StringUtils.hasText(query.status())) {
            wrapper.eq(User::getStatus, query.status());
        }
        if (StringUtils.hasText(query.keyword())) {
            wrapper.likeRight(User::getUsername, query.keyword());
        }
        DataScope.apply(wrapper, DataScopePolicy.ENTIRE_DIRECTORY, User::getCreatedBy);
        applySort(wrapper, query.sortField(), query.sortOrder());
        userMapper.selectPage(page, wrapper);
        return userConverter.toPageResponse(page);
    }

    @Transactional(readOnly = true)
    public UserDetailResponse detail(long id) {
        User user = findById(id);
        return userConverter.toDetail(user);
    }

    @Transactional
    public UserDetailResponse create(UserCreateRequest request) {
        User entity = userConverter.toEntity(request);
        Instant now = Instant.now();
        entity.setIsDeleted(0);
        entity.setDeleteToken(0L);
        entity.setVersion(0);
        entity.setCreatedAt(now);
        entity.setUpdatedAt(now);
        entity.setCreatedBy(AuditContext.currentOperatorId());
        entity.setUpdatedBy(AuditContext.currentOperatorId());
        try {
            userMapper.insert(entity);
        } catch (DuplicateKeyException ex) {
            throw new BusinessException(ErrorCodes.USERNAME_DUPLICATE, "用户名已存在");
        }
        return userConverter.toDetail(entity);
    }

    @Transactional
    public UserDetailResponse update(long id, UserUpdateRequest request) {
        User user = findById(id);
        if (!request.version().equals(user.getVersion())) {
            throw new BusinessException(
                    ErrorCodes.CONCURRENT_MODIFICATION,
                    "用户已被其他请求修改，请刷新后重试",
                    HttpStatus.CONFLICT
            );
        }
        if (request.email() != null) {
            user.setEmail(request.email());
        }
        user.setUpdatedAt(Instant.now());
        user.setUpdatedBy(AuditContext.currentOperatorId());
        int affected = userMapper.updateById(user);
        if (affected != 1) {
            throw new BusinessException(
                    ErrorCodes.CONCURRENT_MODIFICATION,
                    "用户已被其他请求修改，请刷新后重试",
                    HttpStatus.CONFLICT
            );
        }
        // 乐观锁插件已把 version 加一。响应带回这个新值，下一次提交用它。
        return userConverter.toDetail(user);
    }

    @Transactional
    public void delete(long id, UserDeleteRequest request) {
        User user = findById(id);
        if (!request.version().equals(user.getVersion())) {
            throw new BusinessException(
                    ErrorCodes.CONCURRENT_MODIFICATION,
                    "用户已被其他请求修改，请刷新后重试",
                    HttpStatus.CONFLICT
            );
        }
        String beforeSummary = "username=" + user.getUsername() + ",status=" + user.getStatus();
        // 同一事务内先写审计再删数据；审计失败则整体回滚（阻断型操作，见 27-audit-log.md）
        auditRecorder.record(AuditRecordCommand.success(
                "USER_DELETE",
                "User",
                String.valueOf(id),
                beforeSummary
        ));
        Instant now = Instant.now();
        String operatorId = AuditContext.currentOperatorId();
        // 同一次更新写完过滤位、删除令牌、删除时间和删除人。
        // deleteById 只会改 is_deleted，令牌仍是 0，用户名释放不了。
        // 这里没有实体，乐观锁插件不会改这条语句，版本条件写在 Wrapper 里。
        // updateById 由插件处理版本，不要再手写一遍。
        int affected = userMapper.update(null, new LambdaUpdateWrapper<User>()
                .eq(User::getId, user.getId())
                .eq(User::getIsDeleted, 0)
                .eq(User::getVersion, user.getVersion())
                .set(User::getIsDeleted, 1)
                .set(User::getDeleteToken, user.getId())
                .set(User::getDeletedAt, now)
                .set(User::getDeletedBy, operatorId)
                .set(User::getUpdatedAt, now)
                .set(User::getUpdatedBy, operatorId)
                .set(User::getVersion, user.getVersion() + 1));
        if (affected != 1) {
            throw new BusinessException(
                    ErrorCodes.CONCURRENT_MODIFICATION,
                    "用户状态已变化，请刷新后重试",
                    HttpStatus.CONFLICT
            );
        }
    }

    private void applySort(LambdaQueryWrapper<User> wrapper, String sortField, String sortOrder) {
        if (!StringUtils.hasText(sortField)) {
            wrapper.orderByDesc(User::getCreatedAt);
            return;
        }
        SFunction<User, ?> column = SORT_WHITELIST.get(sortField);
        if (column == null) {
            throw new BusinessException(ErrorCodes.INVALID_SORT_FIELD, "非法排序字段");
        }
        if (!"asc".equalsIgnoreCase(sortOrder) && !"desc".equalsIgnoreCase(sortOrder)) {
            throw new BusinessException(ErrorCodes.INVALID_SORT_FIELD, "非法排序方向");
        }
        boolean asc = "asc".equalsIgnoreCase(sortOrder);
        wrapper.orderBy(true, asc, column);
    }

    private User findById(long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw userNotFound();
        }
        DataScope.assertRecord(
                DataScopePolicy.ENTIRE_DIRECTORY,
                String.valueOf(user.getId()),
                user.getCreatedBy(),
                userNotFound()
        );
        return user;
    }

    private static BusinessException userNotFound() {
        return new BusinessException(ErrorCodes.USER_NOT_FOUND, "用户不存在", HttpStatus.NOT_FOUND);
    }

}
