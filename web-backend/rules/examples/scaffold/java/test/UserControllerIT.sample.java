package com.company.product.modules.system.api;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * 集成测试样板（需 Testcontainers 数据源与 SpringBoot 主类）。
 */
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIT {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void page_should_return_total() throws Exception {
        mockMvc.perform(get("/api/v1/system/users?page=1&pageSize=20"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.total").exists())
                .andExpect(jsonPath("$.traceId").exists());
    }
}
