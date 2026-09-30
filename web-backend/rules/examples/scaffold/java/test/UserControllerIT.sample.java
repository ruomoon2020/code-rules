package com.company.product.modules.system.api;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * 集成测试样板（需 Testcontainers 数据源与 SpringBoot 主类）。
 */
@SpringBootTest
@AutoConfigureMockMvc
@WithMockUser(authorities = {
        "system:user:read", "system:user:create", "system:user:update", "system:user:delete",
        "system:audit-log:read"
})
class UserControllerIT {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void page_should_return_total() throws Exception {
        mockMvc.perform(get("/api/v1/system/users?page=1&pageSize=20"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.total").exists())
                .andExpect(jsonPath("$.traceId").exists());
    }

    @Test
    void create_should_return_created_and_location() throws Exception {
        CreatedUser created = createUser("create-alice");

        mockMvc.perform(get("/api/v1/system/users/{id}", created.id()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.version").value(created.version()));
    }

    @Test
    void update_should_use_explicit_post_action() throws Exception {
        CreatedUser created = createUser("update-action-alice");

        mockMvc.perform(post("/api/v1/system/users/{id}/update", created.id())
                        .contentType("application/json")
                        .content(updateBody("updated@example.test", created.version())))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.version").value(created.version() + 1));
    }

    @Test
    void update_should_reject_empty_or_invalid_email() throws Exception {
        mockMvc.perform(post("/api/v1/system/users/1/update")
                        .contentType("application/json")
                        .content("{\"email\":\"not-an-email\",\"version\":0}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @WithMockUser(authorities = "system:user:read")
    void update_without_permission_should_return_forbidden() throws Exception {
        mockMvc.perform(post("/api/v1/system/users/1/update")
                        .contentType("application/json")
                        .content("{\"email\":\"alice@example.test\",\"version\":0}"))
                .andExpect(status().isForbidden());
    }

    @Test
    void delete_should_use_explicit_post_action() throws Exception {
        CreatedUser created = createUser("delete-action-alice");

        mockMvc.perform(post("/api/v1/system/users/{id}/delete", created.id())
                        .contentType("application/json")
                        .content(deleteBody(created.version())))
                .andExpect(status().isNoContent())
                .andExpect(header().exists("X-Trace-Id"));
    }

    @Test
    void same_version_should_allow_only_first_update() throws Exception {
        CreatedUser created = createUser("concurrency-alice");

        mockMvc.perform(post("/api/v1/system/users/{id}/update", created.id())
                        .contentType("application/json")
                        .content(updateBody("first@example.test", created.version())))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.version").value(created.version() + 1));

        mockMvc.perform(post("/api/v1/system/users/{id}/update", created.id())
                        .contentType("application/json")
                        .content(updateBody("second@example.test", created.version())))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.errorCode").value("CONCURRENT_MODIFICATION"));

        mockMvc.perform(get("/api/v1/system/users/{id}", created.id()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.email").value("first@example.test"))
                .andExpect(jsonPath("$.data.version").value(created.version() + 1));
    }

    @Test
    void stale_delete_should_preserve_row_and_roll_back_success_audit() throws Exception {
        CreatedUser created = createUser("stale-delete-alice");
        int currentVersion = created.version() + 1;

        mockMvc.perform(post("/api/v1/system/users/{id}/update", created.id())
                        .contentType("application/json")
                        .content(updateBody("changed@example.test", created.version())))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.version").value(currentVersion));

        mockMvc.perform(post("/api/v1/system/users/{id}/delete", created.id())
                        .contentType("application/json")
                        .content(deleteBody(created.version())))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.errorCode").value("CONCURRENT_MODIFICATION"));

        mockMvc.perform(get("/api/v1/system/users/{id}", created.id()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.version").value(currentVersion));
        expectDeleteAuditCount(created.id(), 0);

        mockMvc.perform(post("/api/v1/system/users/{id}/delete", created.id())
                        .contentType("application/json")
                        .content(deleteBody(currentVersion)))
                .andExpect(status().isNoContent());
        expectDeleteAuditCount(created.id(), 1);

        mockMvc.perform(post("/api/v1/system/users/{id}/delete", created.id())
                        .contentType("application/json")
                        .content(deleteBody(currentVersion)))
                .andExpect(status().isNotFound());
        expectDeleteAuditCount(created.id(), 1);
    }

    @Test
    void legacy_write_methods_should_not_be_exposed() throws Exception {
        mockMvc.perform(patch("/api/v1/system/users/1")
                        .contentType("application/json")
                        .content("{\"email\":\"alice@example.test\",\"version\":0}"))
                .andExpect(status().isMethodNotAllowed());
        mockMvc.perform(delete("/api/v1/system/users/1"))
                .andExpect(status().isMethodNotAllowed());
    }

    private CreatedUser createUser(String username) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/v1/system/users")
                        .contentType("application/json")
                        .content("{\"username\":\"" + username + "\",\"email\":\"alice@example.test\"}"))
                .andExpect(status().isCreated())
                .andExpect(header().exists("Location"))
                .andExpect(jsonPath("$.data.id").isString())
                .andExpect(jsonPath("$.data.version").value(0))
                .andReturn();
        JsonNode data = objectMapper.readTree(result.getResponse().getContentAsString()).path("data");
        return new CreatedUser(data.path("id").asText(), data.path("version").asInt());
    }

    private void expectDeleteAuditCount(String resourceId, int expected) throws Exception {
        mockMvc.perform(get("/api/v1/system/audit-logs")
                        .param("page", "1")
                        .param("pageSize", "20")
                        .param("action", "USER_DELETE")
                        .param("resourceId", resourceId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.total").value(expected));
    }

    private static String updateBody(String email, int version) {
        return "{\"email\":\"" + email + "\",\"version\":" + version + "}";
    }

    private static String deleteBody(int version) {
        return "{\"version\":" + version + "}";
    }

    private record CreatedUser(String id, int version) {}
}
