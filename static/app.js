// Firebase data sources
var leadersRef = new Firebase('https://vdw.firebaseio.com/leaderboard'),
    feedRef = new Firebase('https://vdw.firebaseio.com/feed');

// Angular Controllers
function FeedController($scope) {
    $scope.showLightbox = function(src) {
        document.getElementById('lightboxImage').src=src;
        document.getElementById('lightbox').style.display='inline';
    };

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