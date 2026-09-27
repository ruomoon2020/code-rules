package com.company.product.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Spring Security 样板（非完整可运行）。业务仓须按 JWT/Session 方案补全。
 *
 * <p><strong>复制前必读（企业安全审查要点）</strong>
 *
 * <ul>
 *   <li><strong>CSRF</strong>：仅当<strong>纯 JWT + Authorization Header、无 Session/Cookie 登录</strong>时，才可
 *       {@code csrf.disable()}，且须在 ADR 中说明。若使用 Session、Cookie、表单登录、OAuth2 浏览器流，<strong>必须启用
 *       CSRF</strong>（见 {@code shared/06-security-authz.md}）。
 *   <li><strong>生产 Swagger / Actuator</strong>：禁止 {@code permitAll} 对 {@code /v3/api-docs/**}、{@code
 *       /swagger-ui/**}、敏感 {@code /actuator/**} 公网暴露；仅 dev 可临时放开（evals B40）。
 *   <li>配合 {@code @PreAuthorize}、审计查询 {@code audit:read}、CORS 白名单（evals B39）。
 * </ul>
 *
 * @see rules/shared/06-security-authz.md
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
                // ⚠️ 仅 JWT Header 且无 Cookie 时可禁用；Session/Cookie 场景必须启用 CSRF
                .csrf(csrf -> csrf.disable())
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/actuator/health").permitAll()
                        // ⚠️ 生产禁止 permitAll：仅 dev 可取消下行注释
                        // .requestMatchers("/v3/api-docs/**", "/swagger-ui/**").permitAll()
                        .anyRequest().authenticated()
                )
                .build();
    }
}
