package com.company.product.common.datascope;

/**
 * 数据范围必须由调用方显式选择，禁止用可拼错的资源名字符串推断授权策略。
 */
public enum DataScopePolicy {
    ENTIRE_DIRECTORY,
    OWNER_ONLY
}
