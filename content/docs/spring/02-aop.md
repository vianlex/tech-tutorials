---
title: 第二章 AOP 面向切面编程
linkTitle: AOP 切面编程
description: Spring AOP 的代理原理、切点表达式、通知类型与自调用问题，结合事务与日志等实战场景
weight: 12
---

# AOP 面向切面编程

## 什么是 AOP {#what-is-aop}

AOP（Aspect-Oriented Programming，面向切面编程）把**横切关注点**（如日志、事务、安全、缓存）从业务逻辑中分离出来，避免这些逻辑散落在每个方法里造成重复与散乱。

> [!TIP]
> 日志、事务、权限校验这类逻辑与「业务是什么」无关，却「横切」在大量方法之上，是典型的横切关注点。AOP 让你把它们集中到一处维护，业务方法只关心业务。

AOP 不能替代 OOP，而是对它的补充：OOP 适合纵向的「对象/模块」划分，AOP 适合横向的「横跨多个对象的同一类逻辑」。

## 核心概念 {#concepts}

- **切面（Aspect）**：横切关注点的模块化，如 `LoggingAspect`、`TransactionAspect`。
- **连接点（Join Point）**：程序执行的某个点（Spring AOP 中仅支持「方法执行」这一种连接点）。
- **切点（Pointcut）**：定义在「哪些连接点」上织入通知，是切面的「作用范围」。
- **通知（Advice）**：切面在切点处执行的动作（前/后/环绕等）。
- **织入（Weaving）**：把切面逻辑「缝」进目标代码的过程。Spring 在**运行时**通过代理织入（区别于 AspectJ 的编译期/类加载期织入）。
- **目标对象（Target）**：被增强的原始对象；Spring AOP 中你拿到的往往是它的**代理对象**。

## 底层原理：JDK 动态代理与 CGLIB {#proxy-mechanism}

Spring AOP 的织入本质是「为 Bean 创建一个代理对象，调用时先走代理，再走原方法」。代理有两种实现：

| 代理方式 | 适用条件 | 特点 |
|----------|----------|------|
| JDK 动态代理 | 目标类**实现了接口** | 基于接口生成代理，无需额外依赖 |
| CGLIB | 目标类**没有接口**（或代理类本身） | 基于子类继承生成代理，需字节码增强 |

```text
JDK 代理：Proxy.newProxyInstance(...)  → 实现同一接口
CGLIB 代理：Enhancer.create(...)        → 继承目标类，重写方法
```

**关键变化**：在 Spring Boot 2.x 之前，有接口用 JDK 代理、无接口用 CGLIB；**Spring Boot 3.x 默认统一使用 CGLIB**（`spring.aop.proxy-target-class=true` 已成默认）。好处是行为一致、且能代理没有接口的类。

> [!WARNING]
> CGLIB 通过「继承目标类」生成代理，因此**无法代理 `final` 类与 `final` 方法**（被 final 修饰的方法无法被重写）。若某类需要被 AOP 增强，请勿声明为 final。同时，私有方法也不会被织入。

## 切点表达式语法详解 {#pointcut-syntax}

切点是 AOP 的「瞄准镜」。`execution` 是最常用也最强大的指示器，完整格式为：

```text
execution([修饰符] 返回类型 [包名.类名.]方法名(参数) [异常])
```

逐段说明：

- **修饰符**：可省略（如 `public`），省略表示匹配任意。
- **返回类型**：`*` 匹配任意返回类型；`void`、`String` 匹配具体类型。
- **包/类**：可用 `*` 通配包，`..` 表示「当前包及所有子包」。
- **方法名**：`*` 匹配任意方法。
- **参数**：`()` 无参，`(..)` 任意参数，`(*,String)` 两个参数且第二个为 String。
- **异常**：几乎不写。

```java
// 匹配 com.example.service 包及其子包下，所有 public、返回任意、任意类任意方法、任意参数
@Pointcut("execution(public * com.example.service..*.*(..))")
public void serviceLayer() {}

// 匹配所有以 save 开头、返回 User、接收 Long 参数 的方法
@Pointcut("execution(com.example.entity.User com.example..*.save*(Long))")
public void saveMethods() {}
```

其他常用指示器：

- **`within`**：按「类型所在包/类」匹配（粗粒度，比 execution 快）。

  ```java
  @Pointcut("within(com.example.service..*)") // service 包下所有类的方法
  public void inService() {}
  ```

- **`@annotation`**：按「方法是否带某注解」匹配（最灵活，推荐自定义注解驱动切面）。

  ```java
  @Pointcut("@annotation(com.example.anno.Loggable)") // 标了 @Loggable 的方法
  public void loggable() {}
  ```

- **`args`**：按「运行时参数类型」匹配（注意与 execution 中写死类型不同）。
- **逻辑组合**：切点可用 `&&`、`||`、`!` 组合，如 `serviceLayer() && !loggable()`。

## 各通知类型深入 {#advice-types}

| 通知 | 时机 | 注解 |
|------|------|------|
| 前置 | 方法执行前 | `@Before` |
| 后置返回 | 方法**正常返回后** | `@AfterReturning` |
| 异常 | 方法**抛异常后** | `@AfterThrowing` |
| 最终 | 无论是否异常**都执行**（类似 finally） | `@After` |
| 环绕 | 包裹整个方法，可控制是否执行、修改返回值 | `@Around` |

**`@Around`（最强大）**：通过 `ProceedingJoinPoint.proceed()` 手动决定原方法何时执行，可在前后织入逻辑、改变返回值、吞掉/转换异常：

```java
@Around("serviceLayer()")
public Object around(ProceedingJoinPoint pjp) throws Throwable {
    long start = System.currentTimeMillis();
    try {
        Object result = pjp.proceed();        // 执行原方法（不调用则方法被「拦截」）
        return result;
    } finally {
        long cost = System.currentTimeMillis() - start;
        log.info("{} 耗时 {}ms", pjp.getSignature(), cost);
    }
}
```

**`@AfterReturning` 拿返回值**：通过 `returning` 绑定原方法返回值变量名：

```java
@AfterReturning(pointcut = "serviceLayer()", returning = "ret")
public void afterReturn(JoinPoint jp, Object ret) {
    log.info("{} 返回 {}", jp.getSignature(), ret);
}
```

**`@AfterThrowing` 拿异常**：

```java
@AfterThrowing(pointcut = "serviceLayer()", throwing = "ex")
public void afterThrow(JoinPoint jp, Exception ex) {
    log.error("{} 抛异常", jp.getSignature(), ex);
}
```

> [!WARNING]
> `@Around` 必须**调用 `proceed()` 返回其结果**，否则目标方法不会执行、且返回值丢失。`@Around` 的返回类型应与目标方法一致（通常用 `Object`）。一个切面里同时写 `@Around` 和 `@After` 时，执行顺序为：环绕前 → 前置 → 原方法 → 环绕后 → 最终。

## 多切面顺序与 `@Order` {#aspect-order}

当多个切面作用在同一方法时，需要明确「谁先谁后」。用 `@Order`（值越小越先执行）或实现 `Ordered` 接口：

```java
@Aspect
@Order(1)           // 先执行：事务
@Component
public class TransactionAspect { /* ... */ }

@Aspect
@Order(2)           // 后执行：日志
@Component
public class LoggingAspect { /* ... */ }
```

执行顺序口诀（同一连接点）：**`@Order` 小的，环绕「前」与前置先跑；环绕「后」与后置/最终后跑**。用表格表示（Order 1 先、Order 2 后）：

```text
Order1.@Around前 → Order1.@Before → Order2.@Around前 → Order2.@Before
        → 原方法
Order2.@After/Return → Order2.@Around后 → Order1.@After/Return → Order1.@Around后
```

## 自调用失效问题 {#self-invocation}

这是 AOP 最常见的「坑」：**同一个类内部，方法 A 调用方法 B，若 B 上有切面注解，则该注解不会生效**。

原因：Spring AOP 基于代理。外部调用走的是「代理对象」，代理会先执行切面再转发给目标；而**类内部 `this.b()` 是直接调用原生对象的方法，根本没经过代理**，自然没有增强。

```java
@Service
public class UserService {
    public void register(User u) {
        // ❌ 同类内部调用，save 上的 @Transactional/@Loggable 不生效
        this.save(u);
    }

    @Transactional
    public void save(User u) { /* ... */ }
}
```

**三种解法：**

1. **拆类（最干净）**：把 `save` 抽到另一个 `@Service` 中，让调用跨 Bean（跨代理）自然生效。
2. **注入自身 / 用 ApplicationContext 取代理**：

   ```java
   @Service
   public class UserService {
       private final UserService self; // 注入的是代理对象（自依赖）
       public UserService(UserService self) { this.self = self; }

       public void register(User u) {
           self.save(u); // ✅ 走代理，切面生效
       }
       @Transactional
       public void save(User u) { /* ... */ }
   }
   ```
3. **`AopContext.currentProxy()`**：开启暴露代理后直接取当前代理（需 `@EnableAspectJAutoProxy(exposeProxy = true)`），但不推荐——它把代码与 AOP 基础设施耦合。

> [!TIP]
> 原则：**需要增强的方法，永远从「代理」进入**。最稳妥的设计是让不同职责落在不同 Bean 上。

## 事务与 AOP 的关系 {#transaction-and-aop}

`@Transactional` 本身就是 AOP 的典型实现——Spring 为标注了注解的 Bean 生成代理，在方法执行前开启事务、`proceed()` 后提交、抛异常则回滚。理解这一点，就能解释「为什么同类自调用事务会失效」（见上节）。本章只点出关系，事务细节在第五章展开。

## 实际场景：统一耗时统计与日志 {#real-example}

下面用一个完整切面，演示「接口耗时统计 + 入参脱敏日志」，并配合自定义注解驱动：

```java
// 1) 自定义注解，作为切点触发条件
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Loggable {
    String value() default "";
}

// 2) 切面
@Slf4j
@Aspect
@Component
@Order(10)
public class ApiLogAspect {

    // 切点：任意标了 @Loggable 的方法
    @Pointcut("@annotation(com.example.anno.Loggable)")
    public void loggable() {}

    @Around("loggable() && @annotation(anno)")
    public Object around(ProceedingJoinPoint pjp, Loggable anno) throws Throwable {
        String method = pjp.getSignature().toShortString();
        Object[] args = pjp.getArgs();
        long start = System.currentTimeMillis();
        log.info("[{}] 入参={}", anno.value(), args);
        try {
            Object result = pjp.proceed();
            log.info("[{}] 耗时={}ms 出参={}", anno.value(),
                     System.currentTimeMillis() - start, result);
            return result;
        } catch (Throwable t) {
            log.error("[{}] 异常 耗时={}ms", anno.value(),
                      System.currentTimeMillis() - start, t);
            throw t;
        }
    }
}

// 3) 使用
@Service
public class UserService {
    @Loggable("创建用户")
    public User create(User user) { /* 业务 */ return user; }
}
```

同类思路可复制到**权限校验**（前置检查角色）、**缓存**（环绕里先查缓存再 `proceed`）、**限流/幂等**（环绕里先判令牌）等场景。

## 小结 {#summary}

Spring AOP 在运行时为 Bean 生成（默认 CGLIB）代理，将横切逻辑织入切点匹配的方法；掌握切点表达式、通知顺序与「自调用失效」三大要点，才能把日志、事务、权限等切面写对、写好。下一章学习 Spring MVC——它正是建立在 IoC 与 AOP 之上的 Web 层。
