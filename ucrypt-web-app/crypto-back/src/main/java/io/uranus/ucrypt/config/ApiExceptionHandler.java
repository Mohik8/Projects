package io.uranus.ucrypt.config;

import io.uranus.ucrypt.api.v1.resources.ConstraintViolationResource;
import io.uranus.ucrypt.api.v1.resources.ErrorResource;
import io.uranus.ucrypt.services.exceptions.BusinessException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.dao.InvalidDataAccessApiUsageException;
import org.springframework.dao.PessimisticLockingFailureException;
import org.springframework.data.mapping.PropertyReferenceException;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.multipart.MaxUploadSizeExceededException;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import javax.validation.ConstraintViolationException;
import javax.ws.rs.ForbiddenException;
import java.net.ConnectException;
import java.util.stream.Collectors;

@ControllerAdvice
@Slf4j
public class ApiExceptionHandler extends ResponseEntityExceptionHandler {

    @Value("${spring.servlet.multipart.max-file-size}")
    private String maxFileSize;

    @ExceptionHandler(ConstraintViolationException.class)
    ResponseEntity<ErrorResource> handleConstraintViolationException(final ConstraintViolationException e) {
        final var violations =
                e.getConstraintViolations().stream()
                        .map(
                                violation ->
                                        new ConstraintViolationResource()
                                                .property(violation.getPropertyPath().toString())
                                                .type("ConstraintViolation")
                                                .message(violation.getMessage()))
                        .collect(Collectors.toList());
        log.error(String.format("Constraint violation exception %s", e.getMessage()), e);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResource().message(e.getMessage()).violations(violations));
    }

    @ExceptionHandler(ForbiddenException.class)
    ResponseEntity<ErrorResource> handleForbiddenException(final ForbiddenException e) {
        log.error(String.format("Forbidden operation %s", e.getMessage()), e);
        return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
    }

    @ExceptionHandler(InvalidDataAccessApiUsageException.class)
    ResponseEntity<ErrorResource> handleInvalidDataAccessApiUsageException(final InvalidDataAccessApiUsageException e) {
        log.error(String.format("Invalid request data exception %s", e.getMessage()), e);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResource().message("Request data is not valid").details(e.getMessage()));
    }

    @ExceptionHandler(DataIntegrityViolationException.class)
    ResponseEntity<ErrorResource> handleDataIntegrityViolationException(final DataIntegrityViolationException e) {
        final var errorDetails = e.getMostSpecificCause().getMessage().split("Detail: ");
        final var errorMessage = errorDetails[1].replaceAll("=.*\\)", "");

        log.error(String.format("Data integrity violation exception %s", errorMessage), e);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResource().message(errorMessage));
    }

    @ExceptionHandler(BusinessException.class)
    ResponseEntity<ErrorResource> handleBusinessException(final BusinessException e) {
        log.error(String.format("Business exception %s", e.getMessage()), e);
        return ResponseEntity.status(e.getHttpStatus())
                .body(new ErrorResource().message(e.getMessage())
                        .code(e.getCode()).details(e.getDetails())
                        .extraData(e.getExtraData()));
    }

    @ExceptionHandler(PropertyReferenceException.class)
    ResponseEntity<ErrorResource> handlePropertyReferenceException(final PropertyReferenceException e) {
        log.error(String.format("Property reference exception %s", e.getMessage()), e);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResource().message(e.getMessage()));
    }


    @ExceptionHandler(ConnectException.class)
    ResponseEntity<ErrorResource> handleConnectException(final ConnectException e) {
        log.error(String.format("Connection exception %s", e.getMessage()), e);
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(new ErrorResource().message("external service connection refused"));
    }

    @ExceptionHandler(PessimisticLockingFailureException.class)
    ResponseEntity<ErrorResource> handlePessimisticLockingFailureException(final PessimisticLockingFailureException e) {
        log.error(String.format("lock failure %s", e.getMessage()), e);
        return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE)
                .body(new ErrorResource().message("There's a problem with the application please connect the admin"));
    }

    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(final MethodArgumentNotValidException e, final HttpHeaders headers,
                                                                  final HttpStatus status, final WebRequest request) {
        final var violations = e.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(fieldError -> new ConstraintViolationResource()
                        .property(fieldError.getField())
                        .type("BindingViolation")
                        .message(fieldError.getDefaultMessage()))
                .collect(Collectors.toList());

        log.error(String.format("Method argument not valid exception %s", e.getMessage()), e);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResource().message(e.getMessage()).violations(violations));
    }

    @Override
    protected ResponseEntity<Object> handleHttpMessageNotReadable(final HttpMessageNotReadableException e, final HttpHeaders headers,
                                                                  final HttpStatus status, final WebRequest request) {
        log.error(String.format("HTTP message not readable exception %s", e.getMessage()), e);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResource().message("Error parsing JSON"));
    }

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    ResponseEntity<ErrorResource> handleMaxUploadSizeExceededException(final MaxUploadSizeExceededException e) {
        log.error(String.format("Max upload file exceeded exception %s", e.getMessage()), e);
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResource()
                        .message(String.format("Max uploaded file exceeded, please upload a file less than %s", this.maxFileSize)));
    }

}
