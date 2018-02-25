import click

from timetable_bot.bot import StartBot


@click.command()
@click.option('--start', default=None, help='If the script is launched on the server.')
def main(start):
    """
    Will launch polling or webhooks in accordance with the flag 'start'.
    Default start webhooks
    """
    if start == 'webhooks':
        click.echo('Bot start webhooks!')
        polling = StartBot()
        polling.bot_activation(start)
    elif start == 'polling':
        click.echo('Bot start polling!')
        polling = StartBot()
        polling.bot_activation(start)
    else:
        click.echo('Start error! Please select from \'webhooks\' or \'polling\'.\n'
                   'Example: python manage.py --start [OPTIONS]\n'
                   'If you run the bot on the local machine, select \'polling\'.')


if __name__ == '__main__':
    main()
