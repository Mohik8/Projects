package io.uranus.ucrypt.api.v1;

import io.github.perplexhub.rsql.RSQLJPASupport;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.InvalidMediaTypeException;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.RequestMapping;

@RequestMapping("/api/v1")
public abstract class AbstractController {

    protected static final String TOTAL_COUNT_HEADER = "X-Total-Count";
    protected static final String TOTAL_PAGES_COUNT_HEADER = "X-Total-Pages";
    protected static final int DEFAULT_PAGE_SIZE = 20;

    protected Pageable pageOf(final Integer offset, final Integer limit, final Sort sort) {
        final var size = limit == null ? DEFAULT_PAGE_SIZE : limit;
        final var page = (offset == null ? 0 : offset) / size;
        return PageRequest.of(page, size, sort);
    }

    protected Pageable pageOf(final Integer offset, final Integer limit) {
        return pageOf(offset, limit, Sort.by("id"));
    }

    protected Sort sortBy(final String expr) {
        if (expr == null || expr.isBlank()) {
            return Sort.by("id");
        }

        final var direction = expr.startsWith(">") ? Sort.Direction.DESC : Sort.Direction.ASC;
        final var property = expr.replaceAll("^>|^<", "");

        return Sort.by(direction, property);
    }

    protected <T> Specification<T> specificationFrom(final String query) {
        return RSQLJPASupport.toSpecification(query, true);
    }

    protected MediaType getMimeType(final String type) {
        try {
            return MediaType.parseMediaType(type);
        } catch (InvalidMediaTypeException e) {
            return null;
        }
    }
}
