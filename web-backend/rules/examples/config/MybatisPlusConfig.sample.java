package com.company.product.config;

import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.OptimisticLockerInnerInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.apache.ibatis.mapping.DatabaseIdProvider;
import org.apache.ibatis.mapping.VendorDatabaseIdProvider;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Properties;

/**
 * 样板：分页方言按当前连接识别，不要写死 MySQL 或 PostgreSQL。
 */
@Configuration
public class MybatisPlusConfig {

    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        // 不传 DbType。MySQL 的 LIMIT offset, count 在 PostgreSQL 上是语法错误。
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor());
        // 更新走 @Version 时必须注册。分页只改查询，乐观锁只改更新，先后不影响版本条件。
        interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
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
