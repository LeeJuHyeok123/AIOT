import pygame
import sys
import random

# 초기화
pygame.init()

# 게임 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = 8
        
    def move_left(self):
        if self.x > 0:
            self.x -= self.speed
            
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Ball:
    def __init__(self):
        self.radius = 8
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.dx = random.choice([-5, 5])
        self.dy = -5
        self.speed = 5
        
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        # 벽과 충돌 체크
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.dx = -self.dx
            
        if self.y <= self.radius:
            self.dy = -self.dy
            
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)
                          
    def paddle_collision(self, paddle):
        ball_rect = self.get_rect()
        paddle_rect = paddle.get_rect()
        
        if ball_rect.colliderect(paddle_rect):
            # 패들의 어느 부분에 맞았는지에 따라 반사각 조정
            hit_pos = (self.x - paddle.x) / paddle.width
            self.dx = (hit_pos - 0.5) * 10
            self.dy = -abs(self.dy)
            return True
        return False
        
    def is_out_of_bounds(self):
        return self.y > SCREEN_HEIGHT

class Brick:
    def __init__(self, x, y, color):
        self.width = 75
        self.height = 30
        self.x = x
        self.y = y
        self.color = color
        self.destroyed = False
        
    def draw(self, screen):
        if not self.destroyed:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("벽돌깨기 게임")
        self.clock = pygame.time.Clock()
        
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.score = 0
        self.lives = 3
        self.font = pygame.font.Font(None, 36)
        
        self.create_bricks()
        
    def create_bricks(self):
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        rows = 6
        cols = 10
        
        for row in range(rows):
            for col in range(cols):
                x = col * 80 + 5
                y = row * 35 + 50
                color = colors[row % len(colors)]
                brick = Brick(x, y, color)
                self.bricks.append(brick)
                
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move_right()
            
        return True
        
    def update(self):
        self.ball.move()
        
        # 패들과 공 충돌 체크
        self.ball.paddle_collision(self.paddle)
        
        # 벽돌과 공 충돌 체크
        ball_rect = self.ball.get_rect()
        for brick in self.bricks:
            if not brick.destroyed and ball_rect.colliderect(brick.get_rect()):
                brick.destroyed = True
                self.ball.dy = -self.ball.dy
                self.score += 10
                break
                
        # 공이 바닥에 떨어졌는지 체크
        if self.ball.is_out_of_bounds():
            self.lives -= 1
            if self.lives > 0:
                self.reset_ball()
            else:
                self.game_over()
                
        # 모든 벽돌이 파괴되었는지 체크
        if all(brick.destroyed for brick in self.bricks):
            self.victory()
            
    def reset_ball(self):
        self.ball = Ball()
        
    def game_over(self):
        self.show_message("게임 오버! 스페이스바를 눌러 다시 시작")
        
    def victory(self):
        self.show_message("승리! 스페이스바를 눌러 다시 시작")
        
    def show_message(self, message):
        text = self.font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                        self.restart_game()
                        
    def restart_game(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.score = 0
        self.lives = 3
        self.create_bricks()
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # 게임 객체들 그리기
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        
        for brick in self.bricks:
            brick.draw(self.screen)
            
        # UI 그리기
        score_text = self.font.render(f"점수: {self.score}", True, WHITE)
        lives_text = self.font.render(f"생명: {self.lives}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# 게임 실행
if __name__ == "__main__":
    game = Game()
    game.run()