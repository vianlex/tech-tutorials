---
title: 第五章 数据访问与事务
linkTitle: 数据访问与事务
description: Spring JDBC、Spring Data JPA 与声明式事务管理
weight: 15
---

# 数据访问与事务

## Spring JDBC {#jdbc}

`JdbcTemplate` 封装了 JDBC 的样板代码（连接管理、异常转换、资源释放）：

```java
@Repository
public class UserDao {
    private final JdbcTemplate jdbc;

    public UserDao(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public List<User> findAll() {
        return jdbc.query(
            "SELECT id, name FROM users",
            (rs, rowNum) -> new User(rs.getLong("id"), rs.getString("name"))
        );
    }
}
```

## Spring Data JPA {#jpa}

JPA 是 Java 的 ORM 标准，Spring Data JPA 进一步简化了数据访问：

```java
@Entity
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    // getters / setters
}

// 只需声明接口，Spring 自动实现
public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByNameContaining(String name); // 方法名推导查询
}
```

## 声明式事务 {#transaction}

使用 `@Transactional` 注解，Spring 通过 AOP 自动管理事务：

```java
@Service
public class OrderService {

    @Transactional
    public void placeOrder(Order order) {
        orderRepository.save(order);
        // 扣减库存，若抛异常则整体回滚
        stockService.decrease(order.getItems());
    }
}
```

### 事务传播行为 {#propagation}

| 传播行为 | 说明 |
|----------|------|
| `REQUIRED`（默认） | 有事务则加入，无则新建 |
| `REQUIRES_NEW` | 总是新建独立事务 |
| `NESTED` | 嵌套事务，可局部回滚 |
| `SUPPORTS` | 有则加入，无则非事务执行 |

## 事务失效的常见原因 {#pitfalls}

> [!WARNING]
> 以下情况 `@Transactional` 会失效：
> 1. 同类内部方法自调用（绕过代理）。
> 2. 方法不是 `public`。
> 3. 异常被 `try-catch` 吞掉。
> 4. 抛出的异常类型未被指定回滚。

## 小结 {#summary}

Spring 提供了从 JDBC 到 JPA 的多层数据访问抽象，配合声明式事务，让数据操作既简洁又安全。至此 Spring 核心教程完成，建议动手实践巩固。
