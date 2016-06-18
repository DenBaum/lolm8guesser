from riotwatcher import *
from time import sleep
import logging

log = logging.getLogger('log')

def getTeamOfSummoner( summonerId, game ):
	for p in game['participants']:
		if p['summonerId'] == summonerId:
			return p['teamId']
			
def getSummonerIdsOfOpponentTeam( summonerId, game ):
	teamId = getTeamOfSummoner(summonerId, game)
	summoners = []
	for p in game['participants']:
		if p['teamId'] != teamId:
			summoners.append(p['summonerId'])
	return summoners

def queryPastGameIdSets( w, summonerIds, past10 ):
	sets = {}
	rqs = 0
	for id in summonerIds:
		response = w.get_match_list(id);
		matchlist = []
		if 'matches' in response:
			matchlist = response['matches']
		gamelist = []
		if past10:
			gamelist = w.get_recent_games(id)['games']
			rqs += 2
			if rqs >= 8:
				sleep(10)
				rqs = 0
		log.debug('matches of summoner '+str(id)+': '+str(len(matchlist)))
		s = set()
		for match in matchlist:
			s.add(match['matchId'])
		for game in gamelist:
			s.add(game['gameId'])
		sets[id] = s
	return sets
	
def computeFriendship( IdSets ):
	searchedSets = set()
	friendships = {}
	for id in IdSets:
		friendships[id] = {}
	for id in IdSets:
		searchedSets.add(id)
		for gameId in IdSets[id]:
			for id2 in IdSets:
				if not id2 in searchedSets:
					if gameId in IdSets[id2]:
						if not id2 in friendships[id]:
							friendships[id][id2] = 1
						if not id in friendships[id2]:
							friendships[id2][id] = 1
						friendships[id][id2] += 1
						friendships[id2][id] += 1
	return friendships
	
def computePremades( friendshipRelations ):
	premades = []
	for id in friendshipRelations:
		group = set(friendshipRelations[id].keys())
		group.add(id)
		if group not in premades:
			premades.append(group)
		
	finPremades = []
	for group1 in premades:
		finGroup = group1
		for group2 in premades:
			if group1 != group2 and len(group1 & group2) > 0:
				finGroup = finGroup | group2
		
		if finGroup not in finPremades:
			finPremades.append(finGroup)

	return finPremades
	
def getPremades( summonerName, lolAPIKey, past10 ):
	w = riotwatcher.RiotWatcher(lolAPIKey, default_region=riotwatcher.EUROPE_WEST)
	id = w.get_summoner(name=summonerName)['id']
	game = w.get_current_game(id)
	participants = game['participants']
	idToParticipantsMap = {}
	for p in participants:
		log.info(p['summonerName'].encode('utf8')+' '+str(p['summonerId'])+' '+str(p['teamId']))
		idToParticipantsMap[p['summonerId']] = p
		
	log.debug(getSummonerIdsOfOpponentTeam(id,game))

	gameIdSets = queryPastGameIdSets( w, getSummonerIdsOfOpponentTeam(id,game), past10 )
	friendshipRelations = computeFriendship(gameIdSets)
	log.debug(friendshipRelations)
	
	premades = computePremades(friendshipRelations)
	
	premadesNames = []
	for group in premades:
		groupNames = []
		if len(group) > 1:
			for summonerId in group:
				groupNames.append(idToParticipantsMap[summonerId]['summonerName'])
			premadesNames.append(groupNames)
	
	return premadesNames