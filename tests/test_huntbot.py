from datetime import datetime
import pytest
from unittest.mock import AsyncMock, call, patch

from huntbot.huntbot import (
    date_stats,
    get_values,
    loss,
    reduce_losses,
    reduce_wins,
    overall,
    reset_wins_losses,
    today, 
    win, 
)

@pytest.fixture()
def mock_ctx() -> AsyncMock:
    mock_ctx = AsyncMock()
    mock_ctx.user.name = "is_a_me_mario"
    return mock_ctx


@pytest.fixture(autouse=True)
def reset():
    reset_wins_losses()


async def test_win(mock_ctx: AsyncMock):
    await win.callback(mock_ctx)

    send_message: AsyncMock = mock_ctx.response.send_message
    send_message.assert_has_calls([
        call(f"Congratulations, is_a_me_mario! You have won a game! Today's record is 1 - 0")
    ], any_order=True)

    wins, losses = get_values()
    today = str(datetime.now().date())
    assert wins[today] == 1
    assert losses[today] == 0


async def test_loss(mock_ctx: AsyncMock):
    await loss.callback(mock_ctx)

    send_message: AsyncMock = mock_ctx.response.send_message
    send_message.assert_has_calls([
        call(f"Sorry, is_a_me_mario! You have lost a game! Today's record is 0 - 1")
    ], any_order=True)

    wins, losses = get_values()
    today = str(datetime.now().date())
    assert wins[today] == 0
    assert losses[today] == 1


async def test_get_date(mock_ctx: AsyncMock):
    for _ in range(2):
        await win.callback(mock_ctx)
        await loss.callback(mock_ctx)

    today = str(datetime.now().date())

    await date_stats.callback(mock_ctx, today)
    send_message: AsyncMock = mock_ctx.response.send_message
    send_message.assert_has_calls([
        call(f'On {today}:\nWins: 2\nLosses: 2')
    ], any_order=True)

    wins, losses = get_values()
    assert wins[today] == 2
    assert losses[today] == 2


async def test_overall_stats(mock_ctx: AsyncMock):
    for _ in range(5):
        await win.callback(mock_ctx)
    
    for _ in range(3):
        await loss.callback(mock_ctx)

    await overall.callback(mock_ctx)
    send_message: AsyncMock = mock_ctx.response.send_message
    send_message.assert_has_calls([
        call(f'Overall wins: 5\nOverall losses: 3'),
    ], any_order=True)


async def test_reduce_stuff(mock_ctx: AsyncMock):
    for _ in range(2):
        await win.callback(mock_ctx)
        await loss.callback(mock_ctx)

    today = str(datetime.now().date())
    wins, losses = get_values()
    assert wins[today] == 2
    assert losses[today] == 2

    await reduce_wins.callback(mock_ctx)
    await reduce_losses.callback(mock_ctx)

    send_message: AsyncMock = mock_ctx.response.send_message
    send_message.assert_has_calls([
        call(f'Your wins has been reduced by 1.'),
    ], any_order=True)

    wins, losses = get_values()
    assert wins[today] == 1
    assert losses[today] == 1


@patch("huntbot.huntbot.datetime")
async def test_today_includes_3am(mock_datetime: AsyncMock, mock_ctx: AsyncMock):
    # Populate yesterday with some wins and losses
    yesterday = datetime.fromtimestamp(1682092800)  # 4/21/2023 12:00 pm
    mock_datetime.now.return_value = yesterday
    for _ in range(3):
        await win.callback(mock_ctx)
    for _ in range(6):
        await loss.callback(mock_ctx)
    

    # Set time to 3:58 am
    test_date = datetime.fromtimestamp(1682150280)  # 4/22/2023 3:58 am
    mock_datetime.now.return_value = test_date

    # Add one win and loss to today
    await win.callback(mock_ctx)
    await loss.callback(mock_ctx)

    await today.callback(mock_ctx)
    send_message: AsyncMock = mock_ctx.response.send_message
    send_message.assert_has_calls([
        call(f'You have won 4 games and lost 7 games today.'),
    ], any_order=True)


@patch("huntbot.huntbot.datetime")
async def test_today_does_not_include_4am(mock_datetime: AsyncMock, mock_ctx: AsyncMock):
    # Populate yesterday with some wins and losses
    yesterday = datetime.fromtimestamp(1682092800)  # 4/21/2023 12:00 pm
    mock_datetime.now.return_value = yesterday
    for _ in range(3):
        await win.callback(mock_ctx)
    for _ in range(6):
        await loss.callback(mock_ctx)
    

    # Set time to 3:58 am
    test_date = datetime.fromtimestamp(1682150460)  # 4/22/2023 4:01 am
    mock_datetime.now.return_value = test_date

    # Add one win and loss to today
    await win.callback(mock_ctx)
    await loss.callback(mock_ctx)

    await today.callback(mock_ctx)
    send_message: AsyncMock = mock_ctx.response.send_message
    send_message.assert_has_calls([
        call(f'You have won 1 games and lost 1 games today.'),
    ], any_order=True)
