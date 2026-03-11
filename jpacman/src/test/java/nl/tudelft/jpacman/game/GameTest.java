package nl.tudelft.jpacman.game;

import static org.junit.jupiter.api.Assertions.*;
import nl.tudelft.jpacman.level.Level;
import nl.tudelft.jpacman.level.Player;
import nl.tudelft.jpacman.points.PointCalculator;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.Mockito.*;
class GameTest {
    @Mock
    private PointCalculator pointCalculator;
    @Mock
    private Level level;

    private Game game;

    @BeforeEach
    void setUp(){
        MockitoAnnotations.openMocks(this);
        game = new Game(pointCalculator) {
            @Override
            public List<Player> getPlayers() {
                return Collections.singletonList(mock(Player.class));
            }

            @Override
            public Level getLevel() {
                return level;
            }
        };
}

    @Test
    void testGameAlreadyOn(){
        game.start();
        reset(level);
        game.start();
        verify(level, never()).addObserver(any(Game.class));
        verify(level, never()).start();
    }

    @Test
    void testNoPellets(){
    when(level.isAnyPlayerAlive()).thenReturn(true);
    when(level.remainingPellets()).thenReturn(0);
    game.start();
    assertFalse(game.isInProgress());
    verify(level, never()).addObserver(any(Game.class));
    verify(level, never()).start();
    }

    @Test
    void testAlivePelletsPlayers(){
        when(level.isAnyPlayerAlive()).thenReturn(true);
        when(level.remainingPellets()).thenReturn(1);
        game.start();
        assertTrue(game.isInProgress());
        verify(level).addObserver(game);
        verify(level).start();
    }
}

