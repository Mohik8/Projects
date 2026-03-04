package io.uranus.ucrypt.api.v1;

import io.uranus.ucrypt.api.v1.resources.EmployeesListResource;
import io.uranus.ucrypt.services.EmployeeService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class EmployeeController extends AbstractController implements EmployeesApi {

    private final EmployeeService employeeService;

    @Override
    public ResponseEntity<List<EmployeesListResource>> getEmployees(Integer offset, Integer limit, String sort, String filter) {
        final var employeesPage = this.employeeService.getEmployees(specificationFrom(filter), pageOf(offset, limit, sortBy(sort)));
        return ResponseEntity.ok()
                .header(TOTAL_COUNT_HEADER, String.valueOf(employeesPage.getTotalElements()))
                .header(TOTAL_PAGES_COUNT_HEADER, String.valueOf(employeesPage.getTotalPages()))
                .body(employeesPage.getContent());
    }
}
