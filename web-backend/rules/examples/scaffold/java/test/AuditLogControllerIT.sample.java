package com.company.product.modules.system.api;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * 审计日志集成测试样板（需 Testcontainers 数据源与 SpringBoot 主类）。
 *
 * <p>业务仓接入 Security 后补充：
 * <ul>
 *   <li>无 {@code audit:read} 权限时 {@code GET /audit-logs} 返回 403</li>
 *   <li>契约无 DELETE 审计接口；若误暴露须 404/405</li>
 *   <li>列表/详情 {@code requestSummary} 等字段不含完整证件号等 PII 明文</li>
 * </ul>
 */
@SpringBootTest
@AutoConfigureMockMvc
class AuditLogControllerIT {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void page_should_return_paged_audit_structure() throws Exception {
        mockMvc.perform(get("/api/v1/system/audit-logs?page=1&pageSize=20"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.traceId").exists())
                .andExpect(jsonPath("$.data.page").value(1))
                .andExpect(jsonPath("$.data.pageSize").value(20))
                .andExpect(jsonPath("$.data.total").exists())
                .andExpect(jsonPath("$.data.records").isArray());
    }

    @Test
    void detail_should_return_not_found_when_missing() throws Exception {
        mockMvc.perform(get("/api/v1/system/audit-logs/non-existent-id"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(400))
                .andExpect(jsonPath("$.errorCode").value("AUDIT_LOG_NOT_FOUND"))
                .andExpect(jsonPath("$.traceId").exists());
    }

    @Test
    void delete_should_not_be_supported() throws Exception {
        mockMvc.perform(delete("/api/v1/system/audit-logs/1"))
                .andExpect(status().is4xxClientError());
    }
}
