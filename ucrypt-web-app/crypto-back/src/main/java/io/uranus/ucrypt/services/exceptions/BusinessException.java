package io.uranus.ucrypt.services.exceptions;

import lombok.Getter;
import lombok.Setter;
import org.springframework.http.HttpStatus;

@Getter
@Setter
public class BusinessException extends RuntimeException {
    private final String code;
    private final HttpStatus httpStatus;
    private final String details;
    private final String extraData;

    public BusinessException(final String message, final String code, final HttpStatus httpStatus,
                             final String details, final String extraData) {
        super(message);
        this.code = code;
        this.httpStatus = httpStatus;
        this.details = details;
        this.extraData = extraData;
    }

    public BusinessException(final HttpStatus httpStatus, final String message) {
        super(message);
        this.httpStatus = httpStatus;
        this.code = null;
        this.details = null;
        this.extraData = null;
    }

    public BusinessException(final HttpStatus httpStatus) {
        this.httpStatus = httpStatus;
        this.code = null;
        this.details = null;
        this.extraData = null;
    }
}
