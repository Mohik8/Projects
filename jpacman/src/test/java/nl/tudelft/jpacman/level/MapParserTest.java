package nl.tudelft.jpacman.level;

import static org.junit.jupiter.api.Assertions.*;
import nl.tudelft.jpacman.board.Board;
import nl.tudelft.jpacman.board.BoardFactory;
import nl.tudelft.jpacman.board.Square;
import nl.tudelft.jpacman.npc.Ghost;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
class MapParserTest {

    @Mock
    private LevelFactory levelFactory;

    @Mock
    private BoardFactory boardFactory;

    @InjectMocks
    private MapParser mapParser;

    @BeforeEach
    void setUp(){
        MockitoAnnotations.openMocks(this);
    }
    @Test
    void testParseMapWithOneWall(){
        List<String> lines = List.of("#");
        Square wall = mock(Square.class);
        Board board = mock(Board.class);
        Level level = mock(Level.class);
        when(boardFactory.createWall()).thenReturn(wall);
        when(boardFactory.createBoard(any(Square[][].class))).thenReturn(board);
        when(levelFactory.createLevel(any(Board.class), anyList(), anyList())).thenReturn(level);
        Level result = mapParser.parseMap(lines);
        assertNotNull(result);
    }
}