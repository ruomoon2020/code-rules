package com.company.product.modules.system.infrastructure.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.company.product.modules.system.domain.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
    // 复杂 SQL 在 UserMapper.xml
}
