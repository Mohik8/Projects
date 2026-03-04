package io.uranus.ucrypt.data.repositories;

import io.uranus.ucrypt.data.entities.File;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

import java.util.Optional;


@Repository
public interface FileRepository extends JpaRepository<File, Long>, JpaSpecificationExecutor<File> {
    boolean existsByName(String name);

    Optional<File> findByPath(String path);
}
