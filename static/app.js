// Firebase data sources
var leadersRef = new Firebase('https://vdw2.firebaseio.com/leaderboard'),
    feedRef = new Firebase('https://vdw2.firebaseio.com/feed');

// Angular Controllers
function FeedController($scope) {
    $scope.feed = [];
    feedRef.on('child_added', function(snapshot) {
        $scope.$apply(function() {
            $scope.feed.unshift(snapshot.val());
        });
    });
}

function LeaderboardController($scope) {
    leadersRef.on('child_added', function(snapshot) {
        $scope.$apply(function() {
            $scope.leaders = snapshot.val().leaders;
        });
    });
}