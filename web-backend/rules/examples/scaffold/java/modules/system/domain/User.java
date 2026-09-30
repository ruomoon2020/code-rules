package com.company.product.modules.system.domain;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.Version;

import java.time.Instant;

/**
 * 用户实体（样板）。禁止作为 REST 出参。
 * 默认样板采用单租户（NONE）。项目已有租户列或租户插件时，按项目约定显式补充租户隔离。
 * isDeleted 是唯一的逻辑删除过滤列。deleteToken 未删除为 0，删除时写成主键。
 * deletedAt 只记录删除时间，不参与过滤，也不进入唯一键。自然日用 LocalDate。
 */
@TableName("sys_user")
public class User {

    @TableId
    private Long id;
    private String username;
    private String email;
    private String phone;
    private String status;
    @TableLogic
    @TableField("is_deleted")
    private Integer isDeleted;
    private Long deleteToken;
    private Instant deletedAt;
    private String deletedBy;
    @Version
    private Integer version;
    private Instant createdAt;
    private Instant updatedAt;
    private String createdBy;
    private String updatedBy;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Integer getIsDeleted() { return isDeleted; }
    public void setIsDeleted(Integer isDeleted) { this.isDeleted = isDeleted; }
    public Long getDeleteToken() { return deleteToken; }
    public void setDeleteToken(Long deleteToken) { this.deleteToken = deleteToken; }
    public Instant getDeletedAt() { return deletedAt; }
    public void setDeletedAt(Instant deletedAt) { this.deletedAt = deletedAt; }
    public String getDeletedBy() { return deletedBy; }
    public void setDeletedBy(String deletedBy) { this.deletedBy = deletedBy; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }
    public String getUpdatedBy() { return updatedBy; }
    public void setUpdatedBy(String updatedBy) { this.updatedBy = updatedBy; }
    public Integer getVersion() { return version; }
    public void setVersion(Integer version) { this.version = version; }
}
