from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, shotchartdetail
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc


def get_shot_chart_detail(name, season):
    id = players.find_players_by_full_name(name)[0]["id"]
    career_stats = playercareerstats.PlayerCareerStats(per_mode36="Totals", player_id=id)

    # [0] by season, [1] for total reg season and [2] for total postseason
    totals_by_season = career_stats.get_data_frames()[0]
    team_id = totals_by_season[totals_by_season["SEASON_ID"] == season]["TEAM_ID"]
    shot_chart_detail = shotchartdetail.ShotChartDetail(season_type_all_star="Regular Season", player_id=id,
                                                        team_id=int(team_id), context_measure_simple="FGA",
                                                        season_nullable=season).get_data_frames()

    return shot_chart_detail[0]


def get_shotchart(name, season, clutch=False):
    detail = get_shot_chart_detail(name, season)

    ax = plt.gca()
    plt.axis("off")
    ax.set_xlim(-250, 250)
    ax.set_ylim(422.5, -47.5)

    # court, hoop, and background
    court = Rectangle((-250, -47.5), 500, 470, linewidth=4, color="black", fill=False)
    ax.add_patch(court)
    hoop = Circle((0, 0), radius=7.5, linewidth=2, color="black", fill=False)
    ax.add_patch(hoop)
    backboard = Rectangle((-25, -10), 50, 0, linewidth=2, color="black")
    ax.add_patch(backboard)

    # free throw area
    lane_lines_1 = Rectangle((-80, -47.5), 160, 190, linewidth=2, color="black", fill=False)
    ax.add_patch(lane_lines_1)
    lane_lines_2 = Rectangle((-60, -47.5), 120, 190, linewidth=2, color="black", fill=False)
    ax.add_patch(lane_lines_2)
    free_throw_circle_solid = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=2, color="black")
    ax.add_patch(free_throw_circle_solid)
    free_throw_circle_dashed = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=2, color="black",
                                   linestyle="dashed")
    ax.add_patch(free_throw_circle_dashed)

    # three point line
    three_above_the_break = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=2, color="black")
    ax.add_patch(three_above_the_break)
    left_corner = Rectangle((-220, -47.5), 0, 137, linewidth=2, color="black")
    ax.add_patch(left_corner)
    right_corner = Rectangle((220, -47.5), 0, 137, linewidth=2, color="black")
    ax.add_patch(right_corner)

    # plot shots and add title
    if clutch:
        missed_shots = detail[(detail["EVENT_TYPE"] == "Missed Shot") & (detail["MINUTES_REMAINING"] < 3) &
                              (detail["PERIOD"] == 4)][["LOC_X", "LOC_Y"]]
        made_shots = detail[(detail["EVENT_TYPE"] == "Made Shot") & (detail["MINUTES_REMAINING"] < 3) &
                            (detail["PERIOD"] == 4)][["LOC_X", "LOC_Y"]]
        clutch_percentage = round(len(made_shots)/(len(made_shots) + len(missed_shots)), 2)
        title = f"{name} {season} Regular Season, Clutch FG% = {clutch_percentage}"
    else:
        missed_shots = detail[detail["EVENT_TYPE"] == "Missed Shot"][["LOC_X", "LOC_Y"]]
        made_shots = detail[detail["EVENT_TYPE"] == "Made Shot"][["LOC_X", "LOC_Y"]]
        fg_percentage = round(len(made_shots)/(len(made_shots) + len(missed_shots)), 3)
        title = f"{name} {season} Regular Season, FG% = {fg_percentage}"

    ax.scatter(missed_shots["LOC_X"], missed_shots["LOC_Y"], s=50, color="red", marker="x", linewidths=1)
    ax.scatter(made_shots["LOC_X"], made_shots["LOC_Y"], s=50, edgecolor="green", facecolor="none", marker="o",
               linewidths=1)

    plt.title(title)
    plt.show()


if __name__ == '__main__':
    # data available for 96-97 onwards
    get_shotchart("Demar Derozan", "2021-22", clutch=True)
