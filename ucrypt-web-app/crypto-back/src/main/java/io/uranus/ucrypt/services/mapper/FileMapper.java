package io.uranus.ucrypt.services.mapper;

import io.uranus.ucrypt.api.v1.resources.FileListResource;
import io.uranus.ucrypt.data.entities.File;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface FileMapper {

    FileListResource map(File file);
}
