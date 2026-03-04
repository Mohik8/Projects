package io.uranus.ucrypt.api.v1;

import io.uranus.ucrypt.api.v1.resources.FileDownloadRequestResource;
import io.uranus.ucrypt.api.v1.resources.FileListResource;
import io.uranus.ucrypt.services.FileService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class FileController extends AbstractController implements FilesApi {

    private final FileService fileService;

    @Override
    public ResponseEntity<Void> createFile(final MultipartFile file) {
        this.fileService.createFile(file);
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }

    @Override
    public ResponseEntity<Resource> downloadFile(FileDownloadRequestResource fileDownloadRequestResource) {
        final var downloadFileDto = this.fileService.downloadFile(fileDownloadRequestResource.getFilePath());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=" + downloadFileDto.getFileName())
                .body(downloadFileDto.getFile());
    }

    @Override
    public ResponseEntity<List<FileListResource>> getFiles(final Integer offset, final Integer limit, final String sort, final String filter) {
        final var filesPage = this.fileService.getFiles(specificationFrom(filter), pageOf(offset, limit, sortBy(sort)));
        return ResponseEntity.ok()
                .header(TOTAL_COUNT_HEADER, String.valueOf(filesPage.getTotalElements()))
                .header(TOTAL_PAGES_COUNT_HEADER, String.valueOf(filesPage.getTotalPages()))
                .body(filesPage.getContent());
    }

    @DeleteMapping("/files/{filePath}")
    public ResponseEntity<Void> deleteFile(@PathVariable String filePath) {
        this.fileService.deleteFile(filePath);
        return ResponseEntity.noContent().build();
    }
}
