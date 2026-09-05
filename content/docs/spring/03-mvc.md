---
title: 第三章 Spring MVC
linkTitle: Spring MVC
description: Spring MVC 的请求处理链路、参数绑定、数据校验、统一异常与拦截器过滤器区别
weight: 13
---

# Spring MVC

## 什么是 Spring MVC {#what-is-mvc}

Spring MVC 是 Spring 的 Web 框架，基于 **MVC（Model-View-Controller）** 模式，用于构建 Web 应用和 REST API。其核心是一个前端控制器 `DispatcherServlet`，它把请求统一接收后分发给不同的处理器（Controller），处理完再把响应写回客户端。

在前后端分离的今天，Spring MVC 绝大多数时候以 **REST API** 形式工作：Controller 方法直接返回 JSON（`@RestController`），不再渲染 JSP/Thymeleaf 视图。但 MVC 的「请求→分发→处理→响应」流程依然成立。

## 完整请求处理链路 {#request-flow}

一个请求从浏览器到 Controller 再回到浏览器，会经过 `DispatcherServlet` 协调的一系列组件：

```text
HTTP 请求
   ↓
DispatcherServlet（前端控制器，统一入口）
   ↓
HandlerMapping（根据 URL 找到对应的 Handler/Controller 方法）
   ↓
HandlerAdapter（适配并调用目标方法，完成参数绑定）
   ↓
Controller（执行业务，返回数据或 ModelAndView）
   ↓
HttpMessageConverter（把返回值序列化为 JSON / 视图渲染）
   ↓
HandlerExceptionResolver（若抛异常，统一解析为错误响应）
   ↓
HTTP 响应
```

各组件职责：

- **HandlerMapping**：维护「URL → Handler」的映射，最常用的是 `@RequestMapping` 注册到 `RequestMappingHandlerMapping`。
- **HandlerAdapter**：真正调用处理器，并把 HTTP 参数绑定到方法入参（类型转换、校验在此发生）。
- **HttpMessageConverter**：`@RequestBody` 的 JSON→对象、`@ResponseBody` 的对象→JSON 都靠它（默认 Jackson）。
- **HandlerExceptionResolver**：把 Controller 抛出的异常转换成响应（用 `@ExceptionHandler` 接管）。
- **ViewResolver**：渲染视图时定位模板（REST API 通常不走这一步）。

> [!TIP]
> 理解这条链路的价值：当你遇到「参数绑定失败」「415/400 错误」「异常没被全局捕获」等问题时，能精准定位到是哪个组件出了错，而不是盲目调试。

## 编写控制器 {#controller}

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public User create(@RequestBody User user) {
        return userService.create(user);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

`@RestController` = `@Controller` + `@ResponseBody`，意味着每个方法返回值直接写入响应体（而非视图名）。`@RequestMapping` 的 `produces`/`consumes` 可约束收发内容类型。

## 参数绑定深入 {#parameter-binding}

Spring MVC 提供了丰富的参数绑定注解，由 `HandlerAdapter` 自动完成「HTTP 请求 → 方法参数」的映射：

| 注解 | 来源 | 示例 |
|------|------|------|
| `@PathVariable` | URL 路径片段 | `/users/{id}` → `Long id` |
| `@RequestParam` | 查询参数（?name=x） | `?page=1` → `int page` |
| `@RequestBody` | 请求体（JSON/XML） | POST 的 JSON → `User user` |
| `@RequestHeader` | 请求头 | `Authorization` → `String token` |
| `@CookieValue` | Cookie | `sessionId` → `String` |
| `@ModelAttribute` | 表单字段（非 JSON） | 表单字段 → `UserForm form` |
| `MultipartFile` | 文件上传 | 上传文件 → `MultipartFile file` |

**`@RequestBody` 与 Jackson**：请求体 JSON 经 `MappingJackson2HttpMessageConverter` 反序列化为对象；字段名不匹配可用 `@JsonProperty` 调整，日期可用 `@JsonFormat` 指定格式。

```java
@PostMapping("/upload")
public String upload(
        @RequestParam("file") MultipartFile file,   // 单个文件
        @RequestParam("dir") String dir) {
    if (file.isEmpty()) throw new IllegalArgumentException("文件为空");
    String name = file.getOriginalFilename();
    long size = file.getSize();
    // file.getInputStream() / transferTo(Path) 保存
    return "已上传 " + name + " 大小 " + size;
}
```

> [!WARNING]
> `@RequestParam` 默认 `required=true`，缺失会报 400。可选参数用 `@RequestParam(required = false)` 或声明为 `Optional<String>`。基本类型（int/long）若缺失且无法转换，会直接抛 `TypeMismatchException`。

**`@ModelAttribute` 与 `@RequestBody` 的区别**：前者用于 `application/x-www-form-urlencoded`（表单），后者用于 `application/json`。前端用 JSON 提交却用 `@ModelAttribute` 接收，会得到一堆 null 字段——这是高频错误。

## 数据校验 {#validation}

Spring MVC 集成 Jakarta Bean Validation（`jakarta.validation` 包），在参数绑定后自动执行约束校验。

```java
public class UserForm {
    @NotNull(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "用户名长度 2-20")
    private String username;

    @Email(message = "邮箱格式错误")
    private String email;

    @Min(value = 18, message = "年龄需满 18")
    private Integer age;
    // getters / setters
}
```

**在 Controller 中使用 `@Validated` + `BindingResult`**：

```java
@PostMapping
public ResponseEntity<?> create(@Validated @RequestBody UserForm form,
                                BindingResult result) {
    if (result.hasErrors()) {
        // 手动收集错误，避免抛出 MethodArgumentNotValidException
        List<String> errs = result.getFieldErrors()
            .stream().map(e -> e.getField() + ":" + e.getDefaultMessage())
            .toList();
        return ResponseEntity.badRequest().body(errs);
    }
    return ResponseEntity.ok(userService.create(form));
}
```

若不声明 `BindingResult`，校验失败会抛出 `MethodArgumentNotValidException`，交由全局异常处理器统一转换（见下节）。

**分组校验**：同一实体在不同场景约束不同（如「创建」时 id 可空、「更新」时 id 必填），用校验分组实现：

```java
public interface OnCreate {}   // 分组标记接口
public interface OnUpdate {}

public class UserForm {
    @Null(groups = OnCreate.class)
    @NotNull(groups = OnUpdate.class)
    private Long id;
}

@Validated(OnUpdate.class)   // 指定启用哪组约束
@PutMapping
public User update(@RequestBody UserForm form) { /* ... */ }
```

## 统一响应与异常处理 {#exception-handling}

生产项目需要**统一错误结构**，而不是把异常堆栈直接抛给前端。`@RestControllerAdvice` + `@ExceptionHandler` 是标准做法：

```java
// 1) 统一响应与错误码
public record ApiResult<T>(int code, String message, T data) {
    public static <T> ApiResult<T> ok(T data) { return new ApiResult<>(0, "ok", data); }
    public static ApiResult<Void> fail(int code, String msg) { return new ApiResult<>(code, msg, null); }
}

// 2) 自定义异常体系
public class BizException extends RuntimeException {
    private final int code;
    public BizException(int code, String msg) { super(msg); this.code = code; }
}
public class ResourceNotFoundException extends BizException {
    public ResourceNotFoundException(String msg) { super(404, msg); }
}

// 3) 全局异常处理器
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiResult<Void> handleNotFound(ResourceNotFoundException e) {
        return ApiResult.fail(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResult<List<String>> handleValid(MethodArgumentNotValidException e) {
        List<String> errs = e.getBindingResult().getFieldErrors()
            .stream().map(x -> x.getField() + ":" + x.getDefaultMessage()).toList();
        return ApiResult.fail(400, "参数校验失败");
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResult<Void> handleOther(Exception e) {
        log.error("未捕获异常", e);
        return ApiResult.fail(500, "服务器内部错误");
    }
}
```

要点：

- **异常粒度由细到粗**：具体异常处理器在前，兜底 `Exception` 在后，避免吞掉业务语义。
- **错误码设计**：建议用「业务域+序号」的枚举（如 `USER_NOT_FOUND(1001)`），而不是散落的魔法数字，便于前端与日志定位。
- `@RestControllerAdvice` 默认扫描全部 Controller；可用 `basePackages` 缩小范围。

## 拦截器 vs 过滤器 vs AOP {#filter-interceptor-aop}

三者都能「横切」请求处理，但作用层级不同，选错场景就会失效：

| 维度 | 过滤器 Filter | 拦截器 Interceptor | AOP |
|------|---------------|--------------------|-----|
| 所在层级 | Servlet 容器（最外层） | DispatcherServlet 内部 | Spring Bean 方法级 |
| 能否拿 Spring 上下文 | ❌ 早于容器 | ✅ | ✅ |
| 作用对象 | 所有 HTTP 请求 | 进入 Controller 的请求 | 任意 Spring Bean 方法 |
| 典型用途 | 编码、CORS、XSS 清洗 | 登录校验、权限、日志 | 事务、缓存、方法级日志 |

**`HandlerInterceptor`** 介入的是「请求已到 DispatcherServlet、尚未进入/刚离开 Controller」这一段：

```java
@Component
public class LoginInterceptor implements HandlerInterceptor {

    // 进入 Controller 前：返回 false 则中断请求
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object handler) {
        String token = req.getHeader("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            res.setStatus(HttpStatus.UNAUTHORIZED.value());
            return false;
        }
        return true;
    }

    // Controller 执行后、视图渲染前
    @Override
    public void postHandle(HttpServletRequest req, HttpServletResponse res, Object handler, ModelAndView mv) {}

    // 整个请求完成后（含异常）：做资源清理、耗时统计
    @Override
    public void afterCompletion(HttpServletRequest req, HttpServletResponse res, Object handler, Exception ex) {}
}
```

注册拦截器（并排除登录接口）：

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new LoginInterceptor())
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/login");
    }
}
```

> [!NOTE]
> 经验法则：**与 HTTP 协议本身相关的（编码、CORS、HTTPS 跳转）用 Filter；与「是否放行到 Controller」相关（登录态、鉴权）用 Interceptor；与方法业务逻辑无关的（事务、缓存、方法耗时）用 AOP**。三者可叠加使用，执行顺序：Filter → Interceptor.preHandle → AOP → Controller → Interceptor.postHandle → Interceptor.afterCompletion → Filter。

## 内容协商与 HttpMessageConverter {#content-negotiation}

Spring MVC 支持**内容协商**：同一接口根据请求头 `Accept` 返回不同格式（JSON / XML）。默认由 `HttpMessageConverter` 列表驱动，Jackson 处理 JSON、Jaxb 处理 XML。

- `@ResponseBody` / `@RestController`：表示返回值直接写入响应体，由 Converter 序列化。
- 想同时支持 XML，引入 `jackson-dataformat-xml` 并在 `produces` 中声明 `application/xml` 即可，无需改业务代码。

```java
@GetMapping(value = "/{id}", produces = {"application/json", "application/xml"})
public User getUser(@PathVariable Long id) { return userService.findById(id); }
```

## 小结 {#summary}

Spring MVC 通过 `DispatcherServlet` 把请求分发、参数绑定、校验、序列化、异常处理拆成各司其职的组件，配合拦截器与 AOP 形成完整的 Web 处理链路。下一章学习 Spring Boot——它会把 Controller、配置、内嵌服务器等一切「开箱即用」地组装起来。
