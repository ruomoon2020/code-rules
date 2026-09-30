package com.company.product.common.datascope;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.support.SFunction;
import com.company.product.common.audit.AuditContext;
import com.company.product.common.exception.BusinessException;
import com.company.product.common.exception.ErrorCodes;
import org.springframework.http.HttpStatus;
import org.springframework.util.StringUtils;

/**
 * 列表、详情、修改和删除共用的数据范围。
 * 系统用户和审计样板显式选择整个目录策略，调用仍然不能省。
 * 新的业务资源默认选择按归属人过滤。不要用字符串资源名决定权限，也不要在每个 Mapper 里另写一套条件。
 */
public final class DataScope {

    private DataScope() {}

    public static <T> void apply(
            LambdaQueryWrapper<T> wrapper,
            DataScopePolicy policy,
            SFunction<T, ?> ownerColumn
    ) {
        String operatorId = requireOperator();
        if (policy == DataScopePolicy.ENTIRE_DIRECTORY) {
            return;
        }
        wrapper.eq(ownerColumn, operatorId);
    }

    public static void assertRecord(
            DataScopePolicy policy,
            String resourceId,
            String ownerId,
            BusinessException notFound
    ) {
        String operatorId = requireOperator();
        if (!StringUtils.hasText(resourceId)
                || (policy == DataScopePolicy.OWNER_ONLY && !operatorId.equals(ownerId))) {
            throw notFound;
        }
    }

    private static String requireOperator() {
        String operatorId = AuditContext.currentOperatorId();
        if (!StringUtils.hasText(operatorId)) {
            throw new BusinessException(ErrorCodes.ACCESS_DENIED, "无权访问该记录", HttpStatus.NOT_FOUND);
        }
        return operatorId;
    }
}
