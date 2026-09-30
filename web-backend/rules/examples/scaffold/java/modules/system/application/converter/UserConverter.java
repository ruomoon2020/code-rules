package com.company.product.modules.system.application.converter;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.company.product.common.web.PageResponse;
import com.company.product.modules.system.api.dto.UserCreateRequest;
import com.company.product.modules.system.api.dto.UserDetailResponse;
import com.company.product.modules.system.api.dto.UserSummaryResponse;
import com.company.product.modules.system.domain.User;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

import java.util.List;

/**
 * MapStruct 转换器（样板）。编译后生成实现类。
 */
@Mapper(componentModel = "spring")
public interface UserConverter {

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "phone", ignore = true)
    @Mapping(target = "status", constant = "ENABLED")
    @Mapping(target = "isDeleted", ignore = true)
    @Mapping(target = "deleteToken", ignore = true)
    @Mapping(target = "deletedAt", ignore = true)
    @Mapping(target = "deletedBy", ignore = true)
    @Mapping(target = "version", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "updatedAt", ignore = true)
    @Mapping(target = "createdBy", ignore = true)
    @Mapping(target = "updatedBy", ignore = true)
    User toEntity(UserCreateRequest request);

    @Mapping(target = "id", expression = "java(String.valueOf(user.getId()))")
    UserSummaryResponse toSummary(User user);

    @Mapping(target = "id", expression = "java(String.valueOf(user.getId()))")
    @Mapping(target = "phoneMasked", expression = "java(maskPhone(user.getPhone()))")
    UserDetailResponse toDetail(User user);

    List<UserSummaryResponse> toSummaryList(List<User> users);

    default PageResponse<UserSummaryResponse> toPageResponse(IPage<User> page) {
        return new PageResponse<>(
                (int) page.getCurrent(),
                (int) page.getSize(),
                page.getTotal(),
                toSummaryList(page.getRecords())
        );
    }

    default String maskPhone(String phone) {
        if (phone == null || phone.length() < 7) {
            return phone;
        }
        return phone.substring(0, 3) + "****" + phone.substring(phone.length() - 4);
    }
}
