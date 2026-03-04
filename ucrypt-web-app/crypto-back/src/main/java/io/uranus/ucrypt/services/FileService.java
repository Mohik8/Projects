package io.uranus.ucrypt.services;

import io.uranus.ucrypt.api.v1.resources.FileListResource;
import io.uranus.ucrypt.data.dtos.DownloadFileDto;
import io.uranus.ucrypt.data.entities.File;
import io.uranus.ucrypt.data.entities.User;
import io.uranus.ucrypt.data.repositories.FileRepository;
import io.uranus.ucrypt.data.repositories.UserRepository;
import io.uranus.ucrypt.services.exceptions.BusinessException;
import io.uranus.ucrypt.services.mapper.FileMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class FileService {

    private final FileRepository fileRepository;
    private final User currentUser;
    private final UserRepository userRepository;
    private final FileMapper fileMapper;

    @Value("${files.basic-folder-path}")
    private String FILES_BASIC_FOLDER_PATH;


    /**
     * Creates a file and saves it in the database and the fileSystem.
     *
     * @param file -> file that will be stored in the file system.
     * @throws BusinessException 400 if {@code file} can't be stored in the system;
     */
    @PreAuthorize("hasRole('ADMIN')")
    public void createFile(final MultipartFile file) {
        validateFile(file);

        try {
            final var rootLocation = Paths.get(this.FILES_BASIC_FOLDER_PATH);
            final var uniqueNameForFile = UUID.randomUUID().toString();

            final Path destinationFile = rootLocation.resolve(
                            Paths.get(uniqueNameForFile))
                    .normalize().toAbsolutePath();

            try (final InputStream inputStream = file.getInputStream()) {
                Files.copy(inputStream, destinationFile,
                        StandardCopyOption.REPLACE_EXISTING);
            }

            final File fileEntity = constructFileEntity(file.getOriginalFilename(), destinationFile, file.getContentType());
            this.fileRepository.save(fileEntity);
        } catch (final IOException e) {
            throw new BusinessException(HttpStatus.BAD_REQUEST, "Failed to store file.");
        }
    }

    private void validateFile(final MultipartFile file) {
        if (file.isEmpty()) {
            throw new BusinessException(HttpStatus.BAD_REQUEST, "File is empty, please upload a loaded file");
        }

        final var fileName = file.getOriginalFilename();
        if (fileName == null || fileName.isBlank()) {
            throw new BusinessException(HttpStatus.BAD_REQUEST, "File name is empty, please upload file with a valid name");
        }

        final var fileNameAlreadyExist = this.fileRepository.existsByName(fileName);
        if (fileNameAlreadyExist) {
            throw new BusinessException(HttpStatus.BAD_REQUEST,
                    "File with this name already exists, please upload file with a different name");
        }
    }

    private File constructFileEntity(final String uniqueNameForFile, final Path destinationFile, final String contentType) {
        final var user = this.userRepository.findById(this.currentUser.getId()).orElseThrow();
        return File.builder()
                .name(uniqueNameForFile.replace(" ", "_"))
                .path(destinationFile.getFileName().toString())
                .contentType(contentType)
                .user(user)
                .build();
    }


    /**
     * Returns the file that is saved on system using the id passed to identify which file.
     *
     * @param filePath -> file path.
     * @throws BusinessException 500 if the file couldn't be retrieved from the system;
     * @return the saved file.
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE')")
    public DownloadFileDto downloadFile(final String filePath) {
        final var rootLocation = Paths.get(this.FILES_BASIC_FOLDER_PATH);

        try {
            // Validate and sanitize the file path to prevent path traversal attacks
            if (filePath == null || filePath.trim().isEmpty()) {
                throw new BusinessException(HttpStatus.BAD_REQUEST, "File path cannot be null or empty");
            }
            
            // Check for path traversal patterns
            if (filePath.contains("..") || filePath.contains("./") || filePath.contains("\\")) {
                throw new BusinessException(HttpStatus.BAD_REQUEST, "Invalid file path: path traversal detected");
            }
            
            // Normalize the file path to remove any remaining dangerous patterns
            final String sanitizedPath = Paths.get(filePath).normalize().toString();
            final Path file = rootLocation.resolve(sanitizedPath);
            
            // Ensure the resolved path is still within the root directory
            if (!file.normalize().startsWith(rootLocation.normalize())) {
                throw new BusinessException(HttpStatus.BAD_REQUEST, "Access denied: file path outside allowed directory");
            }
            
            final Resource resource = new UrlResource(file.toUri());
            if (resource.exists() || resource.isReadable()) {
                return constructDownloadFileEntity(resource);
            } else {
                throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR,
                        String.format("Could not read file with path: %s", sanitizedPath));
            }
        } catch (final MalformedURLException e) {
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR,
                    String.format("Could not read file with path: %s", filePath));
        }
    }

    private DownloadFileDto constructDownloadFileEntity(final Resource resource) {
        return DownloadFileDto.builder()
                .fileName(resource.getFilename())
                .file(resource)
                .build();
    }

    /**
     * Returns a paginated result of files that the admin saved based on the pageable object which defines
     * how many rows does a page contain, the page number that should be return and how will the page will be sorted,
     * and the specificationFrom which will filter the data based on specific conditions.
     *
     * @param specificationFrom specification used to filter the data
     * @param pageOf pageable used to paginate the data
     * @return page of files
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE')")
    public Page<FileListResource> getFiles(final Specification<File> specificationFrom, final Pageable pageOf) {
        final var filesPage = this.fileRepository.findAll(specificationFrom, pageOf);
        return filesPage.map(this.fileMapper::map);
    }

    @PreAuthorize("hasRole('ADMIN')")
    public void deleteFile(final String filePath) {
        // Validate and sanitize the file path to prevent path traversal attacks
        if (filePath == null || filePath.trim().isEmpty()) {
            throw new BusinessException(HttpStatus.BAD_REQUEST, "File path cannot be null or empty");
        }
        
        // Check for path traversal patterns
        if (filePath.contains("..") || filePath.contains("./") || filePath.contains("\\")) {
            throw new BusinessException(HttpStatus.BAD_REQUEST, "Invalid file path: path traversal detected");
        }
        
        final var fileEntity = this.fileRepository.findByPath(filePath)
                .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, "File not found"));

        try {
            final var rootLocation = Paths.get(this.FILES_BASIC_FOLDER_PATH);
            final String sanitizedPath = Paths.get(filePath).normalize().toString();
            final Path file = rootLocation.resolve(sanitizedPath).normalize().toAbsolutePath();
            
            // Ensure the resolved path is still within the root directory
            if (!file.startsWith(rootLocation.normalize().toAbsolutePath())) {
                throw new BusinessException(HttpStatus.BAD_REQUEST, "Access denied: file path outside allowed directory");
            }
            
            Files.deleteIfExists(file);
            this.fileRepository.delete(fileEntity);
        } catch (final IOException e) {
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to delete file");
        }
    }
}
