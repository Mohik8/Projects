package io.uranus.ucrypt.data.dtos;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;
import org.springframework.core.io.Resource;

@Getter
@Setter
@Builder
public class DownloadFileDto {

    private String fileName;

    private Resource file;
}
