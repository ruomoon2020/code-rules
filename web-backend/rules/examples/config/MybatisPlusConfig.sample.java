package com.company.product.config;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.apache.ibatis.mapping.DatabaseIdProvider;
import org.apache.ibatis.mapping.VendorDatabaseIdProvider;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Properties;

/**
 * 样板：复制到业务项目并按支持的数据库调整 DbType。
 */
@Configuration
public class MybatisPlusConfig {

    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        // 多库：按当前数据源动态设置，或使用多个 PaginationInnerInterceptor（按项目方案）
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }

    @Bean
    public DatabaseIdProvider databaseIdProvider() {
        VendorDatabaseIdProvider provider = new VendorDatabaseIdProvider();
        Properties props = new Properties();
        props.setProperty("MySQL", "mysql");
        props.setProperty("PostgreSQL", "postgresql");
        provider.setProperties(props);
        return provider;
    }
}
