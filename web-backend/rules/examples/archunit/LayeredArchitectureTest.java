package com.example.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noMethods;

/**
 * 样板：复制到业务项目 src/test/java 并修改包名。
 * 依赖：archunit-junit5
 */
class LayeredArchitectureTest {

    private static final String BASE = "com.company.product";

    private final JavaClasses classes = new ClassFileImporter().importPackages(BASE);

    @Test
    void controller_should_not_depend_on_mapper() {
        ArchRule rule = noClasses()
                .that().resideInAPackage("..api..")
                .should().dependOnClassesThat().resideInAPackage("..mapper..");

        rule.check(classes);
    }

    @Test
    void controller_should_not_depend_on_entity_directly_for_persistence() {
        ArchRule rule = noClasses()
                .that().resideInAPackage("..api..")
                .should().dependOnClassesThat().haveNameMatching(".*Mapper");

        rule.check(classes);
    }

    @Test
    void controller_should_not_use_transactional() {
        ArchRule rule = noMethods()
                .that().areDeclaredInClassesThat().resideInAPackage("..api..")
                .should().beAnnotatedWith(org.springframework.transaction.annotation.Transactional.class);

        rule.check(classes);
    }

    @Test
    void domain_should_not_depend_on_spring_web() {
        ArchRule rule = noClasses()
                .that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAnyPackage("org.springframework.web..");

        rule.check(classes);
    }

    @Test
    void application_should_not_depend_on_api_layer() {
        ArchRule rule = noClasses()
                .that().resideInAPackage("..application..")
                .should().dependOnClassesThat().resideInAPackage("..api..");

        rule.check(classes);
    }
}
