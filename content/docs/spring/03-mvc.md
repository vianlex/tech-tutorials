---
title: 第三章 Spring MVC
linkTitle: Spring MVC
description: Spring MVC 的请求处理流程、控制器与 REST API 开发
weight: 13
---

# Spring MVC

## 什么是 Spring MVC {#what-is-mvc}

Spring MVC 是 Spring 的 Web 框架，基于 **MVC（Model-View-Controller）** 模式，用于构建 Web 应用和 REST API。

## 请求处理流程 {#request-flow}

```text
请求 → DispatcherServlet → HandlerMapping → Controller
                              ↓
响应 ← ViewResolver ← ModelAndView（或 @ResponseBody）
```

1. **DispatcherServlet** 作为前端控制器统一接收请求。
2. **HandlerMapping** 将请求映射到对应的 Controller 方法。
3. Controller 处理业务，返回 `ModelAndView` 或 JSON 数据。

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

## 常用注解 {#annotations}

| 注解 | 作用 |
|------|------|
| `@RestController` | 组合 `@Controller` + `@ResponseBody`，返回 JSON |
| `@RequestMapping` | 映射请求路径 |
| `@GetMapping` / `@PostMapping` | 映射 HTTP 方法 |
| `@PathVariable` | 绑定 URL 路径参数 |
| `@RequestBody` | 绑定请求体 JSON |
| `@RequestParam` | 绑定查询参数 |

## 统一异常处理 {#exception-handling}

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(ResourceNotFoundException e) {
        return new ErrorResponse(404, e.getMessage());
    }
}
```

## 小结 {#summary}

Spring MVC 通过前端控制器模式简化了 Web 开发。下一章学习 Spring Boot，它大幅简化了 Spring 项目的搭建与配置。
