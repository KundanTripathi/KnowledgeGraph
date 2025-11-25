#def main():


from dotenv import load_dotenv
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
from graphiti_core.utils.maintenance.graph_data_operations import clear_data


load_dotenv()


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
neo4j_uri      = os.getenv("NEO4J_URI")
neo4j_user     = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")



graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)

# Episodes list containing both text and JSON episodes
episodes = [
    {
        'content': 'Kamala Harris is the Attorney General of California. She was previously '
        'the district attorney for San Francisco.',
        'type': EpisodeType.text,
        'description': 'podcast transcript',
    },
    {
        'content': 'As AG, Harris was in office from January 3, 2011 – January 3, 2017',
        'type': EpisodeType.text,
        'description': 'podcast transcript',
    },
    {
        'content': {
            'name': 'Gavin Newsom',
            'position': 'Governor',
            'state': 'California',
            'previous_role': 'Lieutenant Governor',
            'previous_location': 'San Francisco',
        },
        'type': EpisodeType.json,
        'description': 'podcast metadata',
    },
    {
        'content': {
            'name': 'Gavin Newsom',
            'position': 'Governor',
            'term_start': 'January 7, 2019',
            'term_end': 'Present',
        },
        'type': EpisodeType.json,
        'description': 'podcast metadata',
    },
]



async def main():
    await clear_data(graphiti.driver)
    await graphiti.build_indices_and_constraints()

    # Add episodes to the graph
    for i, episode in enumerate(episodes):
        await graphiti.add_episode(
            name=f'Freakonomics Radio {i}',
            episode_body=episode['content']
            if isinstance(episode['content'], str)
            else json.dumps(episode['content']),
            source=episode['type'],
            source_description=episode['description'],
            reference_time=datetime.now(timezone.utc),
        )
        print(f'Added episode: Freakonomics Radio {i} ({episode["type"].value})')

    # Perform a hybrid search combining semantic similarity and BM25 retrieval
    print("\nSearching for: 'Who was the California Attorney General?'")
    results = await graphiti.search('Who was the California Attorney General?')

    # Print search results
    print('\nSearch Results:')
    for result in results:
        print(f'UUID: {result.uuid}')
        print(f'Fact: {result.fact}')
        if hasattr(result, 'valid_at') and result.valid_at:
            print(f'Valid from: {result.valid_at}')
        if hasattr(result, 'invalid_at') and result.invalid_at:
            print(f'Valid until: {result.invalid_at}')
        print('---')


asyncio.run(main())

'''
if __name__ == "__main__":
    main()
'''
